$CLASS_INCLUDE$
#include <stdio.h>
$OPTIONAL_INCLUDES$

$OPTIONAL_NAMESPACE$

$OPTIONAL_TYPEDEFS$

unsigned int a;

int main(int argc, char const *argv[])
{
    puts("Dummy main.");

    return 0;
}

void wrapper($PARAMETER_LIST$)
{
    if (a)
    {
      $VARIABLE$;

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
                    "nop;");

      $RETURN_UTILIZATION$;
    }
    else
    {
      $VARIABLE$;
      $FUNCTION_CALL$;
      $RETURN_UTILIZATION$;
    }    

    {
      $VARIABLE$;
      $FUNCTION_CALL$;
      $RETURN_UTILIZATION$;
    }
    {
      $VARIABLE$;
      $FUNCTION_CALL$;
      $RETURN_UTILIZATION$;
    }
    {
      $VARIABLE$;
      $FUNCTION_CALL$;
      $RETURN_UTILIZATION$;
    }
    {
      $VARIABLE$;
      $FUNCTION_CALL$;
      $RETURN_UTILIZATION$;
    }
    {
      $VARIABLE$;
      $FUNCTION_CALL$;
      $RETURN_UTILIZATION$;
    }

    asm volatile("or %rcx, %rcx;");
}