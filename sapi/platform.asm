; =====================================================================
;  SAPI-1 V platform layer for the Bomberman port (replaces the MZ-700
;  monitor ROM and VRAM).
;
;  Hardware (machines/sapi1v.sapi of SAPIemu):
;  - RAM-1V MAP register 63h: C0h = MAP1 = MAP2 = H, CGA-1V at C000h
;    (RAM C000-FFFF hidden, so CP/M is not called during the game);
;  - CGA-1V, EGA mode: 80 bytes per line, 4 pixels per byte (high
;    nibble, D7 left), low nibble = attribute; colour index =
;    attribute * 2 + pixel with COLMASK 1Fh;
;  - MPH-1V at 50h: 82C54 (CLK0 = CLK2 = 55930.4 Hz), YM3812, joystick
;    on K4 (port 54h, active low: D4 fire, D3 left, D2 right, D1 up,
;    D0 down);
;  - Consul 262.3 keyboard on JPR-1V: STROBE pulse on P0-IN0 (port 01h,
;    active low), code on P1 (port 02h, inverted).
; =====================================================================

MAPREG:	equ 063h                ; RAM-1V MAP register
MAP_CGA:	equ 0C0h                ; MAP1 = MAP2 = H
CGA:	equ 0C000h              ; CGA-1V base
CGA_CFG:	equ CGA+03FFBh          ; CONFIG (write), STATUS (read, D7 = VBI)
CGA_PAL_ADDR:	equ CGA+03FFCh          ; Bt476 palette address
CGA_PAL_DATA:	equ CGA+03FFDh          ; Bt476 R, G, B
CGA_COLMASK:	equ CGA+03FFEh          ; Bt476 pixel mask
LINE:	equ 80                  ; bytes per pixel line

PIT0:	equ 050h                ; 82C54 counter 0
PIT2:	equ 052h                ; 82C54 counter 2
PITCW:	equ 053h                ; 82C54 control word (write)
MSTATUS:	equ 053h                ; MPH-1V STATUS (read): D7 F2, D3 T0
MIEN:	equ 054h                ; MPH-1V IEN (write)
JOY:	equ 054h                ; joystick K4 (read)
MIACK:	equ 055h                ; MPH-1V IACK (write)
YMADDR:	equ 056h                ; YM3812 register address
YMDATA:	equ 057h                ; YM3812 data

KSTB:	equ 001h                ; P0-IN: D0 = keyboard STROBE (active low)
KDATA:	equ 002h                ; P1-IN: key code (inverted)

; Timing. One "unit" = one MZ-700 beep loop step (256 x DJNZ + DEC C +
; JR NZ = 3339 T at 3.5469 MHz = 0.94 ms): counter 0 runs in mode 3 with
; 53 (1055 Hz), a unit is one rising edge of OUT0 (STATUS T0).
UNIT_DIV:	equ 53
DELAY_UNITS:	equ 159             ; MZ delay: 5000h x 26 T = 150 ms
; Game frame: 60.8 ms on the MZ-700 (BomberNet docs/port-zx-spectrum.md),
; counter 2 in mode 2 sets F2 every 3400 clocks.
FRAME_DIV:	equ 3400
KEY_HOLD:	equ 2                   ; frames a Consul key press counts as held

; Tone: the MZ-700 8253 counter 0 runs at 1.1088 MHz (PAL models), the
; tone is 1108800 / RATIO Hz. YM3812 F-number = K / (RATIO << block)
; with K = 1108800 * 2^20 / 49716 = 0164D7E0h; the block is chosen so
; that RATIO << block > K >> 10 (= 5936h), then the F-number is < 1024.
TONE_KHI:	equ 05936h              ; K >> 10
; the 10 low bits of K are 1111100000b: the first 5 quotient steps
; shift in 1, the last 5 shift in 0 (see tone_fnum)

; ---- plat_init
; Remember the interrupt state, map the CGA in, set up the palette,
; clear both pages, start the 82C54 counters and the YM3812 voice.
plat_init:
	ld a,i                      ; P/V = IFF2
	di
	ld a,0
	jp po,.pi_di
	inc a
.pi_di:
	ld (saved_iff),a
	ld a,MAP_CGA
	out (MAPREG),a
	ld a,002h                   ; CPU page B, show A, EGA, no IRQ
	ld (CGA_CFG),a
	call cga_clear
	xor a                       ; CPU page A
	ld (CGA_CFG),a
	call cga_clear
	xor a
	ld (CGA_PAL_ADDR),a
	ld hl,palette
	ld b,palette_end-palette
.pi_pal:
	ld a,(hl)
	ld (CGA_PAL_DATA),a
	inc hl
	djnz .pi_pal
	ld a,01Fh                   ; index = P4..P0 (attribute, pixel)
	ld (CGA_COLMASK),a
	ld a,036h                   ; counter 0: LSB+MSB, mode 3
	out (PITCW),a
	ld a,UNIT_DIV
	out (PIT0),a
	xor a
	out (PIT0),a
	ld a,0B4h                   ; counter 2: LSB+MSB, mode 2
	out (PITCW),a
	ld a,FRAME_DIV & 0FFh
	out (PIT2),a
	ld a,FRAME_DIV >> 8
	out (PIT2),a
	ld a,028h                   ; IEN: gates G2 and G0, no interrupts
	out (MIEN),a
	ld a,0C0h                   ; clear F2 and F1
	out (MIACK),a
	ld hl,ym_init
.pi_ym:
	ld a,(hl)                   ; register, value pairs, FFh ends
	inc a
	jr z,.pi_end
	dec a
	inc hl
	ld e,(hl)
	inc hl
	call ym_write
	jr .pi_ym
.pi_end:
	xor a
	ld (key_code),a
	ld (key_left),a
	ret

; YM3812 channel 0: modulator (slot 0) with feedback for a buzzy tone,
; carrier (slot 3) at full level, sustained while the key is on.
ym_init:
	defb 001h,020h              ; WSE
	defb 008h,000h
	defb 0BDh,000h
	defb 020h,021h, 023h,021h   ; EG-TYP sustain, MULT 1
	defb 040h,01Ch, 043h,004h   ; levels
	defb 060h,0F0h, 063h,0F0h   ; attack fast, no decay
	defb 080h,00Fh, 083h,00Fh   ; sustain level 0, fast release
	defb 0E0h,000h, 0E3h,000h   ; sine
	defb 0C0h,00Ch              ; feedback 6, FM
	defb 0B0h,000h              ; key off
	defb 0FFh

; ---- plat_exit
; Back to CP/M: silence, unmap the CGA, restore interrupts, warm boot.
plat_exit:
	call MSTP
	xor a
	out (MAPREG),a
	ld a,(saved_iff)
	or a
	jr z,.px_di
	ei
.px_di:
	jp 0

saved_iff:
	defb 0

; ---- cga_clear
; Fill the CPU page of the CGA (0000-3E7F) with 00h (black).
cga_clear:
	ld hl,CGA
	ld de,CGA+1
	ld bc,16000-1
	ld (hl),0
	ldir
	ret

; ---- ym_write
; YM3812 register A = E. The chip needs 12 of its clocks after the
; address and 84 after the data (3.3 us and 23.5 us, 94 T at 4 MHz).
ym_write:
	out (YMADDR),a
	ex (sp),hl                  ; 19 T x 2
	ex (sp),hl
	ld a,e
	out (YMDATA),a
	push bc
	ld b,7                      ; 7 x 13 T
.yw_wait:
	djnz .yw_wait
	pop bc
	ret

; ---- MSTA
; Start the tone 1108800 / (RATIO) Hz (MZ-700 monitor MSTA). Keeps all
; registers except AF.
MSTA:
	push bc
	push de
	push hl
	ld de,(RATIO)
	ld a,d
	or e
	jr nz,.ms_nz
	dec de                      ; 0 = 65536 on the 8253, take 65535
.ms_nz:
	ld b,0                      ; block
.ms_blk:
	ld hl,TONE_KHI
	or a
	sbc hl,de
	jr c,.ms_div                ; DE > K >> 10: F-number fits
	ld a,b
	cp 7
	jr z,.ms_max
	inc b
	ex de,hl                    ; DE <<= 1
	add hl,hl
	ex de,hl
	jr .ms_blk
.ms_max:
	ld hl,1023                  ; too high for the YM3812
	jr .ms_set
.ms_div:
	push bc
	push ix                     ; the game keeps record pointers in IX
	call tone_fnum
	pop ix
	pop bc
.ms_set:
	ld a,0A0h                   ; F-number low
	ld e,l
	call ym_write
	ld a,b                      ; KEY ON, block, F-number high
	add a,a
	add a,a
	or h
	or 020h
	ld e,a
	ld a,0B0h
	call ym_write
	pop hl
	pop de
	pop bc
	ret

; ---- tone_fnum
; HL = K / DE, where K >> 10 < DE (so the quotient has 10 bits).
tone_fnum:
	ld ix,0                     ; quotient
	ld hl,TONE_KHI              ; remainder = K >> 10
	ld b,10
.tf_loop:
	add ix,ix
	ld a,b
	cp 6
	ccf                         ; CY = next bit of K (1 for b = 10..6)
	adc hl,hl
	jr c,.tf_big                ; remainder >= 65536 > DE
	or a
	sbc hl,de
	jr nc,.tf_one
	add hl,de
	jr .tf_next
.tf_big:
	or a
	sbc hl,de
.tf_one:
	inc ix
.tf_next:
	djnz .tf_loop
	push ix
	pop hl
	ret

; ---- MSTP
; Stop the tone (MZ-700 monitor MSTP).
MSTP:
	push de
	ld a,0B0h
	ld e,0
	call ym_write
	pop de
	ret

RATIO:
	defw 0

; ---- wait_units
; Wait C units (0.95 ms each, C = 0 means 256), polling the keyboard.
wait_units:
	call poll_key
	in a,(MSTATUS)              ; wait for OUT0 low
	and 008h
	jr nz,wait_units
.wu_high:
	call poll_key
	in a,(MSTATUS)              ; then for the rising edge
	and 008h
	jr z,.wu_high
	dec c
	jr nz,wait_units
	ret

; ---- frame_wait
; Wait for the 60.8 ms frame tick (F2), polling the keyboard; then
; age the held key.
frame_wait:
	call poll_key
	in a,(MSTATUS)
	rlca                        ; CY = F2
	jr nc,frame_wait
	ld a,080h                   ; clear F2
	out (MIACK),a
	ld a,(key_left)
	or a
	ret z
	dec a
	ld (key_left),a
	ret

; ---- poll_key
; Catch a Consul key press (STROBE is a 1 ms pulse, not latched): the
; code counts as held for KEY_HOLD frames. ESC or BREAK ends the game.
poll_key:
	in a,(KSTB)
	rrca
	ret c                       ; STROBE inactive
	in a,(KDATA)
	cpl
	cp 01Bh                     ; ESC
	jp z,plat_exit
	and 0FEh
	cp 084h                     ; BREAK (84h, 85h)
	jp z,plat_exit
	in a,(KDATA)
	cpl
	ld (key_code),a
	ld a,KEY_HOLD
	ld (key_left),a
	ret

key_code:
	defb 0
key_left:
	defb 0

; ---- key_fire
; A = 20h (MZ space) when the joystick fire or the space key is held,
; else 0. Replaces GETKY where the game asks for SPACE.
key_fire:
	in a,(JOY)
	and 010h
	ld a,020h
	ret z
	call held_key
	cp 020h
	ret z
	xor a
	ret

; ---- key_dir
; A = MZ cursor code (11h down, 12h up, 13h right, 14h left) from the
; joystick or the Consul cursor keys, else 0. Replaces GETKY in
; move_player.
key_dir:
	in a,(JOY)
	rrca
	ld a,011h
	ret nc                      ; D0 down
	in a,(JOY)
	and 002h
	ld a,012h
	ret z                       ; D1 up
	in a,(JOY)
	and 004h
	ld a,013h
	ret z                       ; D2 right
	in a,(JOY)
	and 008h
	ld a,014h
	ret z                       ; D3 left
	call held_key
	cp 0C1h
	jr c,.kd_none
	cp 0C5h
	jr nc,.kd_none
	push hl                     ; C1 up, C2 down, C3 right, C4 left
	push de
	sub 0C1h
	ld l,a
	ld h,0
	ld de,.kd_map
	add hl,de
	ld a,(hl)
	pop de
	pop hl
	ret
.kd_none:
	xor a
	ret
.kd_map:
	defb 012h,011h,013h,014h

; ---- held_key
; A = the Consul code still held (KEY_HOLD frames after the press), or 0.
held_key:
	ld a,(key_left)
	or a
	ret z
	ld a,(key_code)
	ret
