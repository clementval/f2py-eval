SUBROUTINE test
  !$claw loop-fusion
  !$claw loop-interchange
  !$claw looooop-fusion
  !$acc parallel
  !$acc end parallel
END SUBROUTINE test
