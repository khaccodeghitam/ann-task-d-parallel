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
find_package(Python3 REQUIRED COMPONENTS Interpreter)
enable_testing()
add_test(NAME task_da_contract COMMAND ${Python3_EXECUTABLE} -m unittest discover
  -s tests/research -p test_task_da.py -v)
set_tests_properties(task_da_contract PROPERTIES
  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/../.."
  ENVIRONMENT "TASK_DA_SMOKE=$<TARGET_FILE:task_da_smoke>"
  TIMEOUT 60)
