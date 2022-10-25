ORG 0H            
LJMP MAIN
STRING1:  DB "adrian" ; string data 
DB 0  ;; Null termination 
STRING1_L: DB 6 
STRING2:  DB "gomez" ;; string data 
DB 0  ;; Null termination  
STRING2_L:  DB 5
;--------------STRCPY----------------
STRCPY:
MOV A,R0	;Moving Address
MOV R1,A	;Moved into R1
MOV R3,#0	;Clearing R3

FORLOOP:	; To cycle through each character
MOV A,R3
MOVC A,@A+DPTR
;pointer goes through all the characters
JZ ENDS
;once done, goes to next function 
MOV @R0,A
INC R3		;; increments character
INC R0		;; increments pointer
SJMP FORLOOP ;will keep going thru each letter

ENDS: 	;Jumps here when null or at the end 
MOV @R0,#0h 
MOV A,R1
MOV R0,A ;Returning Destination address into R0
MOV A,R3
RET			;;Returns to Caller Funct

;------- STRCONCAT -------------
STRCONCAT: 
MOV DPTR,#STRING1		; Loading the address of STRING1 to DPTR

Call STRCPY 
MOV B,A ; Copy A into B  
MOV DPTR,#STRING2 	; Loading the address of STRING2 to DPTR
ADD A,R0      ;Adding string1_L with r0
MOV R0,A

Call STRCPY
ADD A,B 	;Adding both strings
RET 	;Return to Caller Function


;-------------TESTSTRING------------
TESTSTRING: 
call STRCONCAT 
MOV B,A		; Moving the sum from A to B
MOV DPTR,#STRING1_L
MOV A,#0	 ;Clearing A
MOVC A,@A+DPTR 
MOV R1,A		;Moving into R1
MOV DPTR,#STRING2_L
MOV A,#0
MOVC A,@A+DPTR
ADD A,R1 
;Got the length of the strings, now to compare
JNZ Comp_String
; if the Difference of lengths are not zero, jump to Comp_String, otherwise add and jump to success
ADD A,B  
JZ SUCCESS 
;---------- COMPARE_STRINGS--------
;Comparing and storing strings
Comp_String:
MOV R2,A  
CJNE A,B,ERROR 	;Comparing, if error jump
MOV A,R0  
MOV R3,#0		;Clearing
MOV R5,#0 

;-------COMPARE_S1_L------------
; Comparision of String1 Length
Comp_String_1:
MOV DPTR,#STRING1_L
MOV B,R5  
MOV A,#0
MOVC A,@A+DPTR ;Getting the String Length
JZ Z_String_2 ;Jump to String 2 if String 1 is NULL.
DEC A ;Decrementing until it hits 0
SUBB A,B   
JC Z_String_2 ;When string1 length is equal to zero, compare String2
MOV A,R5  
MOV DPTR,#STRING1		;Make a copy of string
MOVC A,@A+DPTR
MOV B,A  ;Copy from A to B 
;Create new string and storing into A
MOV A,R3  
MOV R1,#60h 
ADD A,R1  
MOV R1,A
MOV A,@R1 	;String now stored in A
CJNE A,B,ERROR		; if A doesnt have B go to ERROR
INC R3  
INC R5
; Moving pointer until done
 SJMP Comp_String_1

Z_String_2:
 MOV R5,#0  

;-------COMPARE_S2_L------------
; Same as Comparing String 1 Length
COMPARE_STRING2:
MOV DPTR,#STRING2_L
MOV B,R5  
MOV A,#0
MOVC A,@A+DPTR 
JZ SUCCESS
DEC A
SUBB A,B   
JC SUCCESS
MOV A,R5  
MOV DPTR,#STRING2
MOVC A,@A+DPTR
MOV B,A  
MOV A,R3 
MOV R1,#60H
ADD A,R1 
MOV R1,A
MOV A,@R1 
CJNE A,B,ERROR
INC R5
INC R3   
DJNZ R2,COMPARE_STRING2 
SJMP SUCCESS
;------- Main Function ---------
MAIN: 
MOV R0, #60H 
Call TESTSTRING 
SUCCESS: SJMP SUCCESS 
ERROR: SJMP ERROR  
END
