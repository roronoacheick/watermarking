import string

def cesar_cipher(text, key, cipher):
	if type(text) == str and type(key) == int:
		shift = 1 if cipher else -1
		list_of_crypted_chars = []
		for char in text :
			list_of_crypted_chars.append(chr((ord(char) + shift * key) % 1_114_112))

		crypted_text = "".join(list_of_crypted_chars)
		return crypted_text
	else:
		raise(TypeError)


def hack_cesar_cipher(crypted_text, alphabet):
	if type(crypted_text) == str and type(alphabet) == str:
		for possible_key in range(0, 1_114_112):
			possible_uncryption = cesar_cipher(crypted_text, possible_key, cipher=False)
			if possible_uncryption[0] in alphabet:
				print(possible_key)
				print(possible_uncryption)
				print("_"*20)
	else:
		raise(TypeError)


def vigenere_cipher(text, password, cipher):
	list_of_crypted_chars = []
	list_of_keys = [ord(char) for char in password]
	
	for index, current_char in enumerate(text):
		
		current_key = list_of_keys[index % len(list_of_keys)]
		current_crypted_char = cesar_cipher(current_char, current_key, cipher)

		list_of_crypted_chars.append(current_crypted_char)

	crypted_text = "".join(list_of_crypted_chars)

	return crypted_text




from PIL import Image
import numpy as np


try:
	image = Image.open("Les_pilliers.png")
except FileNotFoundError:
	print("Erreur : Impossible de trouver l'image")
	exit()

image.show()
image_np = np.array(image)

x ,y = 50, 100
pixel = image_np [y, x]
print(f"Valeur du pixel à ({x}, {y}) : {pixel}")

if len(pixel) == 3:
	 print(f"Rouge : {pixel[0]}, Vert : {pixel[1]}, Bleu : {pixel[2]}")
else:
	print("Pixel en niveaux de gris :", pixel)

print("Dimensions de l'image :", image_np.shape)


gray_image = image.convert("L") 
gray_image.show()
gray_np = np.array(gray_image)
print("Dimensions de l'image en gris :", gray_np.shape)

even_image = gray_np.copy()
even_image[even_image % 2 != 0] -= 1
Image.fromarray(even_image).show()
print("Pixel original (50,100) :", gray_np[50, 100])
print("Pixel transformé en pair (50,100) :", even_image[50, 100])


def text_to_binary(message):
	return ''.join(format(ord(c), "08b") for c in message)





if __name__ == "__main__":
	message = "le chocolat est bon"

	crypted_text = cesar_cipher(message, 12, cipher=True) # exo 1Ò
	print(crypted_text)

	initial_message = cesar_cipher(crypted_text, 12, cipher=False) # exo 2
	print(initial_message == message)

	hack_cesar_cipher(crypted_text, alphabet=string.printable) # exo3

	crypted_message = vigenere_cipher(text=message, password="Azerty12345!", cipher=True)
	print(crypted_message)
	initial_message = vigenere_cipher(text=crypted_message, password="Azerty12345!", cipher=False)
	print(initial_message)