$CLASS_INCLUDE$
#include <stdio.h>
$OPTIONAL_INCLUDES$

$OPTIONAL_NAMESPACE$

$OPTIONAL_TYPEDEFS$

unsigned int a;
unsigned int b;

int main(int argc, char const *argv[])
{
    puts("Dummy main.");

    return 0;
}

void wrapper($PARAMETER_LIST$)
{
    $VARIABLE$;
    
    for (unsigned int i = 0; i < a; i++)
    {
      if (a > b) break;
      else
      {

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

        $RETURN_UTILIZATION$;
      }
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