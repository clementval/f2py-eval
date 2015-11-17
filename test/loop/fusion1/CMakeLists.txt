set (ORIGINAL_FILE original_code.f90)
set (OUTPUT_FILE transformed_code.f90)
set (REFERENCE_FILE reference.f90)

set (EXECUTABLE_ORIGINAL original_code_fusion1)
set (EXECUTABLE_TRANSFORMED transformed_code_fusion1)


# Transform
add_custom_command(
  OUTPUT  ${OUTPUT_FILE}
  COMMAND ${CLAW_C} -i ${ORIGINAL_FILE} -o ${OUTPUT_FILE}
  DEPENDS ${ORIGINAL_FILE}
COMMENT "Parsing file")

add_custom_target(transform-fusion1 ALL
  DEPENDS ${OUTPUT_FILE})

add_executable (${EXECUTABLE_ORIGINAL} ${ORIGINAL_FILE})
add_executable (${EXECUTABLE_TRANSFORMED} ${OUTPUT_FILE})

add_test(NAME python-transform-fusion1 COMMAND diff ${OUTPUT_FILE} ${REFERENCE_FILE})
