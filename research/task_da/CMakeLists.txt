cmake_minimum_required(VERSION 3.20)
project(task_da LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(SANITIZER "" CACHE STRING "Optional address,undefined")
if(SANITIZER)
  add_compile_options(-fsanitize=${SANITIZER} -fno-omit-frame-pointer -g)
  add_link_options(-fsanitize=${SANITIZER})
endif()
add_compile_options(-Wall -Wextra -Wpedantic -Werror)
add_executable(task_da_smoke search_common/smoke.cpp)
find_package(Threads REQUIRED)
add_executable(task_da_p1_eval search_common/p1_eval.cpp)
target_link_libraries(task_da_p1_eval PRIVATE Threads::Threads)
add_executable(task_da_p2_eval search_common/p2_eval.cpp)
target_link_libraries(task_da_p2_eval PRIVATE Threads::Threads)
add_executable(task_da_p2_trace_eval search_common/p2_eval.cpp)
target_compile_definitions(task_da_p2_trace_eval PRIVATE TASK_DA_ROUND_TRACE=1)
target_link_libraries(task_da_p2_trace_eval PRIVATE Threads::Threads)
add_executable(task_da_h3_offline_cost h3_assignment_cost.cpp)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
enable_testing()
add_test(NAME task_da_contract COMMAND ${Python3_EXECUTABLE} -m unittest discover
  -s tests/research -p test_task_da.py -v)
set_tests_properties(task_da_contract PROPERTIES
  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/../.."
  ENVIRONMENT "TASK_DA_SMOKE=$<TARGET_FILE:task_da_smoke>;TASK_DA_P1_EVAL=$<TARGET_FILE:task_da_p1_eval>;TASK_DA_P2_EVAL=$<TARGET_FILE:task_da_p2_eval>"
  TIMEOUT 60)
add_test(NAME h3_trace_contract COMMAND ${Python3_EXECUTABLE} -m unittest discover
  -s tests/research -p test_h3_overlap.py -v)
set_tests_properties(h3_trace_contract PROPERTIES
  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/../.."
  ENVIRONMENT "TASK_DA_P2_EVAL=$<TARGET_FILE:task_da_p2_eval>;TASK_DA_P2_TRACE_EVAL=$<TARGET_FILE:task_da_p2_trace_eval>"
  TIMEOUT 60)
