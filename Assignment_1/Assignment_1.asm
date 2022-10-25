ORG 50H
ARRAY1: DB 10, 5, 120, 255, 240, 70, 40, 255 ; array a
ORG 60H
ARRAY2: DB 5, 20, 2, 50, 100, 240, 250, 200 ; array x
ORG 0

MOV R0, #3H ;N
MOV A,R0	; Values for N in ACC

;Puts 0 in Registers
MOV R3,#0 
MOV R4,#0
MOV R5,#0  

MOV B,#1	;Starts at first element

;loop extensions

L1: CJNE A,B, L2
;L2 tests if there is a carry bit
L2: JC finish

 
;adding results block

;indexing
MOV A,B ;initalizing i
ADD A,#-1
MOV R1,A ;storing value of i
	
;accessing arrays

;accessing array 1
MOV DPTR,#ARRAY1;access values in array A
MOV A,R1 ; moving i into A
MOVC A,@A+DPTR ; get value
MOV B,A ;copy value back to B

;acessing array 2
MOV DPTR,#ARRAY2 ;access values in array X
MOV A,R1 ;moving i into ACC
MOVC A,@A+DPTR ;get value


;got 2 numbers, now to multiply

;each loop will add the older value

	
;multiplication of numbers
MOV R7,#0     ;clearing r7

MUL AB
MOV R2,A		; least sig. 
MOV R6,B		; most sig.

;adding multiplied numbers
MOV A,R3
ADD A,R2
MOV R3,A

MOV A,R4
ADDC A,R6
MOV R4,A

MOV A,R5
ADDC A,R7
MOV R5,A


INC R1 
INC R1 ; adjusting i
MOV B,R1


MOV A,R0  ;moving element we want into A

SJMP L1  ; short jump back to loop

finish:
END
