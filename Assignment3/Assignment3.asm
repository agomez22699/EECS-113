;Studnet ID:20119988
;Name: Adrian Gomez
;Date:05/10/2020

RS EQU P3.3 ;RS signal
E EQU P3.1 ;E signal
ORG 0 
	JMP Main	;Jumps to Main
ORG 3
	JMP ExternalInt		;Jumps to External Interrupt
ORG 0BH 
	JMP TimerInt  ;Jumps to Timer Interrupt
ORG 30H 
	JMP Main		;Jumps to Main
;====== External Retrieval ========
e_Retrieval:		;; Keeping places from conversion
	MOV A,R3 	;Moving R3 into A
	MOV B, #2	;Moving 2 into B
	MUL AB
	MOV B,#10	;Moving 10 into B
	DIV AB 		
	MOV R4, A	;Storing value into R4
	MOV R7, B  	;Storing value into R7
	;Determined Ones Place
	MOV A, R2 	;Storing R2 into A 
	MOV B, #2	;Moving 2 into B
	MUL AB
	ADD A, R4	;Adding A with R4
	MOV B, #10
	DIV AB
	MOV R5, A	;Storing A into R5
	MOV R4, B	;Storing B into R4
	;Determined Tenths Place
	MOV B, #2
	MOV A, R1 ;store r1 into A
	MUL AB
	ADD A, R5
	MOV B, #10
	DIV AB
	MOV R5, B	;Storing B into R5
	;Determined Hundreths Place
	RET 
;;=========== Delay ================
Delay:
	MOV R0, #50			;Makes sure LCD can be updated
	DJNZ R0, $      
	RET	
;;========= Pulsing =================
Pulsing:
	SETB E 				;Setting E to 1
	CLR E				;Setting E to 0
	CALL Delay
	RET					; Return to Caller
;;===== Send Character ===========
SendCharacter:
	MOV P1,A	;Sending Characters
	Call Pulsing
	RET			; Return to caller
;======== Start of External Interrupt ============
ExternalInt:  
	CLR P3.7	;Enabling Data
	MOV A,P2	;Moves data from ADC to ACC
	SETB P3.7	;Disabling Data 
	CALL bin_to_decimal		;; Converts binary to decimal
	CALL e_Retrieval		;Stores Values
	SETB RS		;displaying to LCD	
	MOV A, R5	;First Value
	ADD A, #48	;ASCII conversion
	CALL SendCharacter
	MOV A, #'.'	;Decimal Point
	CALL SendCharacter
	MOV A, R4	;Second Value
	ADD A, #48
	CALL SendCharacter
	MOV A, R7	;Third Value
	ADD A, #48
	CALL SendCharacter 
	CLR RS		;Move cursor to beginning
	MOV P1,#10h	;Shifts Once
	CALL Pulsing	;Calling Pulse
	MOV P1,#10h	
	CALL Pulsing	
	MOV P1,#10h	
	CALL Pulsing
	MOV P1,#10h	
	CALL Pulsing	
	RETI		;Returns from Interrupt
;;======= Timer Interrupt =========
TimerInt:		;Reading ADC Values
	SETB IT0	;Setting External Interrupt to 1
	SETB EX0	;Enabling External Interrupt
	CLR P3.6	;Clearing ADC Write Line
	SETB P3.6 
	CPL P1.2
	MOV TL0, #0F0H	
	MOV TH0,#0D8H	
	RETI		;Returns from Interrupt
;;========= LCD SETUP ================
Setup_LCD:		;Setup LCD display
	CLR RS		;Sending Instructions
	MOV P1,#38H 	;Set Data_L to 8 bits, 2 lines, 5x7 Char. Font.
	CALL Pulsing
	MOV P1,#06H 	;Increment, No Shift
	CALL Pulsing
	MOV P1,#0FH			;Display  ON, Cursor ON, and Blinking ON
	Call Pulsing
	RET
;======= Bin to Decimal Conversion ==========
bin_to_decimal:
	MOV B,#100
	DIV AB
	MOV R1,A ;Ones Place  ---- Storing into Register R1
	MOV A,B
	MOV B,#10
	DIV AB
	MOV R2,A ;first decimal  ---- Storing into Register 2
	MOV R3,B ;second decimal ---- Storing into Register 3
	RET

;;=========== START OF MAIN ===============  
Main:
	CALL Setup_LCD ;initialize LCD
	MOV TMOD, #01H	;Timer Mode 1
	MOV TL0, #0F0H
	MOV TH0,#0D8H	;10ms Timer
	MOV IE, #82H	;Enable Timer Interrupt
	SETB TR0	;Start the Timer	
	SETB EA		
	SJMP $		; Stay at this line until interrupt
