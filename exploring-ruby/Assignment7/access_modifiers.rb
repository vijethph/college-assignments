class BankAccount
  attr_reader :account_number, :balance

  def initialize(account_number, initial_balance, pin)
    @account_number = account_number
    @balance = initial_balance
    @pin = pin
    @transaction_history = []
  end

  def deposit(amount)
    if amount > 0
      @balance += amount
      record_transaction("Deposit", amount)
      puts "Deposited $#{amount}. New balance: $#{@balance}"
      true
    else
      puts "Invalid deposit amount"
      false
    end
  end

  def withdraw(amount, pin)
    if verify_pin(pin)
      if amount > 0 && amount <= @balance
        @balance -= amount
        record_transaction("Withdrawal", amount)
        puts "Withdrew $#{amount}. New balance: $#{@balance}"
        true
      else
        puts "Invalid amount or insufficient funds"
        false
      end
    end
  end

  def transfer(amount, pin, target_account)
    if verify_pin(pin)
      if amount > 0 && amount <= @balance
        if process_transfer(amount, target_account)
          puts "Transferred $#{amount} to account #{target_account.account_number}"
          true
        else
          puts "Transfer failed"
          false
        end
      else
        puts "Invalid amount or insufficient funds"
        false
      end
    end
  end

  def check_balance(pin)
    if verify_pin(pin)
      puts "Current balance: $#{@balance}"
      @balance
    end
  end

  def view_history(pin)
    if verify_pin(pin)
      display_transaction_history
    end
  end

  def change_pin(old_pin, new_pin)
    if verify_pin(old_pin)
      update_pin(new_pin)
    end
  end

  def to_s
    "Account ##{@account_number} | Balance: $#{@balance}"
  end

  protected

  def verify_pin(pin)
    if @pin == pin
      true
    else
      puts "Invalid PIN"
      false
    end
  end

  def process_transfer(amount, target_account)
    @balance -= amount
    target_account.receive_transfer(amount, self)
    record_transaction("Transfer out", amount)
    true
  end

  def receive_transfer(amount, from_account)
    @balance += amount
    record_transaction("Transfer in from ##{from_account.account_number}", amount)
    puts "Received $#{amount} from account #{from_account.account_number}"
  end

  private

  def record_transaction(type, amount)
    @transaction_history << {
      timestamp: Time.now,
      type: type,
      amount: amount,
      balance: @balance
    }
  end

  def display_transaction_history
    puts "\n--- Transaction History for Account ##{@account_number} ---"
    if @transaction_history.empty?
      puts "No transactions yet"
    else
      @transaction_history.each_with_index do |txn, idx|
        puts "[#{idx + 1}] #{txn[:timestamp].strftime('%Y-%m-%d %H:%M')} | #{txn[:type]}: $#{txn[:amount]} | Balance: $#{txn[:balance]}"
      end
    end
    puts "-" * 60
  end

  def update_pin(new_pin)
    @pin = new_pin
    puts "PIN successfully changed"
    true
  end
end

puts "Bank Account - Public, Protected, Private Methods Demo"
puts "="*70

account1 = BankAccount.new("ACC001", 1000, "1234")
account2 = BankAccount.new("ACC002", 500, "5678")

puts "\n--- Public Methods ---"
puts "\n1. Creating accounts and checking toString:"
puts account1
puts account2

puts "\n2. Deposit:"
account1.deposit(500)

puts "\n3. Withdraw (requires PIN):"
account1.withdraw(200, "1234")
account1.withdraw(200, "wrong")

puts "\n4. Check Balance (requires PIN):"
account1.check_balance("1234")
account1.check_balance("wrong")

puts "\n5. Transfer (requires PIN):"
account1.transfer(300, "1234", account2)

puts "\n6. View History (requires PIN):"
account1.view_history("1234")

puts "\n7. Change PIN (requires old PIN):"
account1.change_pin("1234", "9999")
account1.check_balance("9999")


puts "\n--- Protected Methods ---"


begin
  account1.verify_pin("9999")
rescue NoMethodError => e
  puts "Error: #{e.message}"
end

puts "\n--- Private Methods ---"

puts "\nTrying to call private method directly from outside:"
begin
  account1.record_transaction("Test", 100)
rescue NoMethodError => e
  puts "Error: #{e.message}"
end



puts "\n--- Final Account States ---"
account1.view_history("9999")
account2.view_history("5678")
