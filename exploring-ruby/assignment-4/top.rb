require_relative 'book'
require_relative 'user'
require_relative 'library'

book1 = Book.new("To Kill a Mockingbird", "Harper Lee", "B001", "978-0061120084", "Fiction", 1960)
book2 = Book.new("1984", "George Orwell", "B002", "978-0451524935", "Dystopian", 1949)
book3 = Book.new("The Great Gatsby", "F. Scott Fitzgerald", "B003", "978-0743273565", "Fiction", 1925)
book4 = Book.new("Pride and Prejudice", "Jane Austen", "B004", "978-0141439518", "Romance", 1813)
book5 = Book.new("The Catcher in the Rye", "J.D. Salinger", "B005", "978-0316769174", "Fiction", 1951)

user1 = User.new("Alice Johnson", "123 Main St, Dublin", "U001", "alice@email.com", "555-0101")
user2 = User.new("Bob Smith", "456 Oak Ave, Cork", "U002", "bob@email.com", "555-0102")
user3 = User.new("Carol Williams", "789 Pine Rd, Galway", "U003", "carol@email.com", "555-0103")

library = Library.new("City Central Library")

library.add_book(book1)
library.add_book(book2)
library.add_book(book3)
library.add_book(book4)
library.add_book(book5)

library.add_user(user1)
library.add_user(user2)
library.add_user(user3)

puts "\nInitial Library State"
library.show_status
library.show_all_books
library.show_all_users

puts "\n\nBorrowing Event 1"
puts "\nAlice Johnson borrows '1984'..."
library.borrow_book("U001", "B002")

puts "\nLibrary state after borrowing:"
library.show_status
puts "\nBook status:"
puts "  #{book2}"
puts "\nUser status:"
puts "  #{user1}"

puts "\n\nBorrowing Event 2"
puts "\nBob Smith borrows 'The Great Gatsby'..."
library.borrow_book("U002", "B003")

puts "\nLibrary state after borrowing:"
library.show_status

puts "\n\nBorrowing Event 3"
puts "\nAlice Johnson borrows 'To Kill a Mockingbird'..."
library.borrow_book("U001", "B001")

puts "\n\nCurrent State"
library.show_status
library.show_all_books
library.show_all_users

puts "\n\nAdditional Feature: Search by Genre"
library.search_books_by_genre("Fiction")

puts "\n\nBook Return Event"
puts "\nAlice Johnson returns '1984'..."
library.return_book("U001", "B002")

puts "\nFinal library state:"
library.show_status
library.show_all_books
