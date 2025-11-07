def calculate_and_display_no_require(x, y, z)
  sum = add_numbers(x, y)
  product = multiply_numbers(sum, z)

  formatted_sum = format_result(sum)
  formatted_product = format_result(product)

  display_message("Sum: #{x} + #{y} = #{formatted_sum}")
  display_message("Product: #{sum} * #{z} = #{formatted_product}")
  display_message("Final calculation: (#{x} + #{y}) * #{z} = #{product}")

  product
end

calculate_and_display_no_require(5, 3, 4)