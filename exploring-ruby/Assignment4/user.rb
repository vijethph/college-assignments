class User
  attr_accessor :name, :address, :unique_id, :email, :phone, :borrowed_books, :borrow_limit

  def initialize(name, address, unique_id, email, phone)
    @name = name
    @address = address
    @unique_id = unique_id
    @email = email
    @phone = phone
    @borrowed_books = []
    @borrow_limit = 3
  end

  def can_borrow?
    @borrowed_books.length < @borrow_limit
  end

  def borrow_book(book_id)
    @borrowed_books << book_id
  end

  def return_book(book_id)
    @borrowed_books.delete(book_id)
  end

  def to_s
    borrowed_info = @borrowed_books.empty? ? "None" : @borrowed_books.join(", ")
    "User ID: #{@unique_id} | Name: #{@name} | Address: #{@address} | Borrowed Books: #{borrowed_info}"
  end
end
