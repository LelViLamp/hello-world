#' Use the value if test is positive and use fallback value instead.
#' 
#' @description This function is a simple wrapper around a test function. If the
#' test function returns TRUE, the value is returned, otherwise the fallback
#' value is returned.
#' 
#' @author LelViLamp
#'
#' @param value The value to be tested and returned if the test function is TRUE.
#' @param test_fn The function that will be used to test the value.
#' @param fallback The value to be returned if the test function is FALSE.
#'
#' @return The value if the test function is TRUE, otherwise the fallback value.
#' @export
#'
#' @examples
#' fallback_if_false(1, is.numeric, 42) # returns 1
#' fallback_if_false("oh dear, a string, let's panic", is.numeric, 42) # returns 42
#' fallback_if_false(NULL, is.numeric, 42) # returns 42
fallback_if_false <- function(value, test_fn, fallback) {
  if (test_fn(value) == TRUE)
    return(value)
  else
    return(fallback)
}
