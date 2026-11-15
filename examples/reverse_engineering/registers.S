/* A leaf function using the System V AMD64 ABI; only caller-saved registers. */
.intel_syntax noprefix
.text
.globl register_demo
.type register_demo, @function
register_demo:
    mov rax, -1
    mov eax, 0x12345678
    mov al, 0x7f
    lea rcx, [rdi + 4]
    mov edx, DWORD PTR [rdi]
    ret
.size register_demo, .-register_demo
.section .note.GNU-stack,"",@progbits
