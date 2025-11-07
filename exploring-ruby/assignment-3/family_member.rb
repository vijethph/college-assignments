class FamilyMember
  attr_accessor :name, :sex, :status, :age, :children

  def initialize(name, sex, status, age, children = [])
    @name = name
    @sex = sex
    @status = status
    @age = age
    @children = children
  end

  def parent?
    if @children.empty?
        return false
    end

    case @sex
    when "male"
      "father"
    when "female"
      "mother"
    else
      "parent"
    end
  end

  def child?
    if @age >= 18 && @status != "dependent"
        return false
    end

    case @sex
    when "male"
      "son"
    when "female"
      "daughter"
    when "dog"
      "dog"
    else
      "child"
    end
  end
end

fm1 = FamilyMember.new("John", "male", "married", 45, ["Alice", "Bob"])
fm2 = FamilyMember.new("Mary", "female", "married", 42, ["Alice", "Bob"])
fm3 = FamilyMember.new("Alice", "female", "student", 16, [])
fm4 = FamilyMember.new("Bob", "male", "dependent", 12, [])
fm5 = FamilyMember.new("Rex", "dog", "pet", 3, [])

puts "#{fm1.name} is parent: #{fm1.parent?}"
puts "#{fm1.name} is child: #{fm1.child?}"
puts "#{fm2.name} is parent: #{fm2.parent?}"
puts "#{fm2.name} is child: #{fm2.child?}"
puts "#{fm3.name} is parent: #{fm3.parent?}"
puts "#{fm3.name} is child: #{fm3.child?}"
puts "#{fm4.name} is parent: #{fm4.parent?}"
puts "#{fm4.name} is child: #{fm4.child?}"
puts "#{fm5.name} is parent: #{fm5.parent?}"
puts "#{fm5.name} is child: #{fm5.child?}"

family_members = [fm1, fm2, fm3, fm4, fm5]

puts "\nFamily Members List:"
family_members.each do |member|
  status_type = case member.status
  when "married"
    "married"
  when "student", "dependent"
    "underage"
  else
    "single"
  end

  puts "Name: #{member.name}, Status: #{status_type}"
end

puts "\nComplete Family Member Information:"
family_members.each do |member|
  puts "=" * 40
  puts "Name: #{member.name}"
  puts "Sex: #{member.sex}"
  puts "Status: #{member.status}"
  puts "Age: #{member.age}"
  puts "Children: #{member.children.empty? ? 'None' : member.children.join(', ')}"
end