CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -pedantic -O2
SRC = main.c scanner.c token.c token_types.c errors.c util.c
OBJ = $(SRC:.c=.o)
TARGET = minic_scanner

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJ)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ) $(TARGET)

.PHONY: all clean
