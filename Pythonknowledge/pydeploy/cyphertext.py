#!/usr/bin/python35
from optparse import Option, OptionParser
from simplecrypt import encrypt, decrypt

#Usage - Encrypt: python35 ${scriptName} -e "PlainText" ==> Displays cyphercode for the input "PlainText"
#Usage - Decrypt: python35 $0  ==> Displays the planeText of cyphercode given below.
cyphercode=b'sc\x00\x02\xb4\xdc%3`\x80@Sh\x82\xa0\x0e\x9e\x1c>\xa2\x98W\x9b\xd5\x8c\xa4a"\xfa\x0b\x904"\x0f\x85\x99\xf2<\x83U\xf3\xde\xd1\xea\xe2\x8f\xfd\x1aU\xdbH\xd8\xed\xa3\r7\xecM\xff\xda\xa7\xde8?\xcc\xaf\xff\x0f\xd7\xf2\x97\xf0+\x10\xc6\xa8\xb2\xb7'

PARSER_DEFAULTVAL = True
def get_opt_parser():
    parser = OptionParser()
    parser.add_option('-d', '--decrypt', help='Input ciphercode to decrypt', default='decrypt')
    parser.add_option('-e', '--encrypt', help='Input string to encrypt')
    return parser

opt_parser = get_opt_parser()
(opts, args) = opt_parser.parse_args()
opts_dict = vars(opts)
if __name__ == "__main__":
   if opts_dict['encrypt']:
       ciphertext = encrypt('password', opts_dict['encrypt'])
       print("Encrypted String = %s" %ciphertext)

   if opts_dict['decrypt']:
       decryptedSrting = decrypt('password',cyphercode).decode('ascii') 
       print("Decrypted String = %s" %decryptedSrting)
