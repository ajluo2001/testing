#include <stdio.h>
#include <ctype.h>
 
int main(int argc, char* argv[]) {
   if (argc != 2)
   {
       fprintf(stderr, "You need 1 argument!\n");
       return 1;
   }
   //Find the pointers to beginning of the string
   char *beginning = argv[1];
 
   //Find the pointer to the end of the string
  
   char *ending = beginning;
   while (*ending != '\0')
   {
       ending++;
   }
   ending--;
  
   int ispalindrome = 0;
   while (ending > beginning)
   {
      char begchar = *beginning;
      char endchar = *ending;

      int begalnum = isalnum(begchar);
      int endalnum = isalnum(endchar);
      
      //if is alphanumeric, turn lowercase
      if (begalnum == 1) 
      {
          begchar = tolower(begchar);
      }
      if (endalnum == 1)
      {
          endchar = tolower(endchar);
      }
      
      if (begalnum == 1 && endalnum == 1)
      {
          if (endchar != begchar)
          {
              ispalindrome=1;
          }
          beginning++;
          ending--;
      }
      else if (begalnum == 1 && endalnum == 0)
      {
          ending--;
      }
      else if (begalnum == 0 && endalnum == 1)
      {
          beginning++;
      }
      else 
      {
          beginning++;
          ending--;
      }

   }
   
   //if palindrome, return 0
   if (ispalindrome == 0)
   {
       return 0;
   }
   else //if not palindrome, ispalindome == 1, then return 1
   {
       return 1;
   }
 
   return 0;
}
