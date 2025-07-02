# 1. Encapsulation
class Person:
    def _init_(self, name, age):
        self.name = name        # Public attribute
        self.__age = age        # Private attribute
    
    def get_age(self):
        return self.__age  # Getter method

# 2. Overloading (Using default arguments)
class MathOperations:
    def add(self, a, b, c=0):  # Overloading using default values
        return a + b + c

# 3. Inheritance
class Employee(Person):
    def _init_(self, name, age, salary):
        super()._init_(name, age)  # Calling parent class constructor
        self.salary = salary
    
    def show_details(self):
        print(f"Name: {self.name}, Age: {self.get_age()}, Salary: {self.salary}")

# Taking input from user
name = input("Enter person's name: ")
age = int(input("Enter person's age: "))
p = Person(name, age)
print("Person's Age:", p.get_age())  # Accessing private attribute via getter

# Taking input for overloading
a = int(input("Enter first number: "))
b = int(input("Enter second number: "))
c = input("Enter third number (or press Enter to skip): ")
math_op = MathOperations()
if c:
    print("Sum of three numbers:", math_op.add(a, b, int(c)))
else:
    print("Sum of two numbers:", math_op.add(a, b))

# Taking input for inheritance
emp_name = input("Enter employee's name: ")
emp_age = int(input("Enter employee's age: "))
emp_salary = float(input("Enter employee's salary: "))
emp = Employee(emp_name, emp_age, emp_salary)
emp.show_details()