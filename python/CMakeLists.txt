include(GrPython)

if(NOT PYTHONINTERP_FOUND)
  return()
endif()

GR_PYTHON_INSTALL(
  FILES __init__.py
  doppler.py
  multiple_source.py
  MsgPairToVar.py
  DESTINATION ${GR_PYTHON_DIR}/doppler
)
