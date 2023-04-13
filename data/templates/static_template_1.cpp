$CLASS_INCLUDE$
#include <stdio.h>
$OPTIONAL_INCLUDES$

$OPTIONAL_NAMESPACE$

$OPTIONAL_TYPEDEFS$

int main(int argc, char const *argv[])
{
    puts("Dummy main.");

    return 0;
}

void wrapper($PARAMETER_LIST$)
{
    $VARIABLE$;

    puts("Start.");

    asm volatile ("or %rax, %rax;"
                  "or %rax, %rax;"
                  "or %rax, %rax;");

    $FUNCTION_CALL$;

    asm volatile ("nop;"
                  "or %rbx, %rbx;"
                  "or %rbx, %rbx;"
                  "or %rbx, %rbx;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;"
                  "nop;");

    puts("End.");

    $RETURN_UTILIZATION$;

    asm volatile("or %rcx, %rcx;");
}