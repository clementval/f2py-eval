PROGRAM f2py_eval
  CALL test
END PROGRAM f2py_eval

SUBROUTINE test
  INTEGER :: i
  INTEGER :: istart = 1
  INTEGER :: iend = 10
  !$claw loop-fusion
  DO i = istart, iend
    print*,'body loop 1', i
  END DO

  !$claw loop-fusion
  DO i = istart, iend
    print*,'body loop 2', i
  END DO

  !$claw loop-fusion
  DO i = istart, iend
    print*,'body loop 3', i
  END DO
END SUBROUTINE test
