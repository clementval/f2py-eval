  ! Simple program to test the loop-fusion directive

  PROGRAM loop_fusion
    CALL clawloop
  END PROGRAM loop_fusion

  SUBROUTINE clawloop()
    INTEGER i
    !$claw loop-fusion
    DO i=1,10
      PRINT *, 'First loop body:', i
      PRINT *, 'Second loop body:', i
      PRINT *, 'Third loop body:', i
    END DO 



  END SUBROUTINE clawloop