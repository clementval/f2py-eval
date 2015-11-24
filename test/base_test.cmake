set (ORIGINAL_FILE original_code.f90)
set (OUTPUT_FILE transformed_code.f90)
set (REFERENCE_FILE reference.f90)
set (EXECUTABLE_ORIGINAL original_code_${TEST_NAME})
set (EXECUTABLE_TRANSFORMED transformed_code_${TEST_NAME})

# Transform with claw_c.py
add_custom_command(
  OUTPUT  ${OUTPUT_FILE}
  COMMAND ${CLAW_C} -i ${ORIGINAL_FILE} -o ${OUTPUT_FILE}
  DEPENDS ${ORIGINAL_FILE}
  COMMENT "Parsing file with claw_c.py"
)

add_custom_target(
  transform-${TEST_NAME}
  ALL
  DEPENDS ${OUTPUT_FILE}
)

add_executable (${EXECUTABLE_ORIGINAL} ${ORIGINAL_FILE})
add_executable (${EXECUTABLE_TRANSFORMED} ${OUTPUT_FILE})

add_test(
  NAME python-transform-${TEST_NAME}
  COMMAND diff ${OUTPUT_FILE} ${REFERENCE_FILE}
)

if (V2)
  set (OUTPUT_FILE_V2 transformed_code_v2.f90)
  set (EXECUTABLE_TRANSFORMED_V2 transformed_code_${TEST_NAME}_v2)
  set (REFERENCE_FILE_V2 reference_v2.f90)

  # Transform with claw_c_v2.py
  add_custom_command(
    OUTPUT  ${OUTPUT_FILE_V2}
    COMMAND ${CLAW_C_V2} -i ${ORIGINAL_FILE} -o ${OUTPUT_FILE_V2}
    DEPENDS ${ORIGINAL_FILE}
    COMMENT "Parsing file with claw_c_v2.py"
  )

  add_custom_target(
    transform-${TEST_NAME}-v2
    ALL
    DEPENDS ${OUTPUT_FILE_V2}
  )

  add_executable (${EXECUTABLE_TRANSFORMED_V2} ${OUTPUT_FILE_V2})

  add_test(
    NAME python-transform-${TEST_NAME}-v2
    COMMAND diff ${OUTPUT_FILE_V2} ${REFERENCE_FILE_V2}
  )

endif()
