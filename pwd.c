#include <stdio.h>
#include <sys/stat.h>
#include <dirent.h>
#include <unistd.h>

int main()

{
    //stat struct
    struct stat statstruct;

    //dirent struct
    struct dirent *structdirent;
    
    //this will track the current inode number, we stop loop when this equals 2
    int inode; 

    DIR* dir;


    if (lstat(".", &statstruct) == -1)
      {
          perror("");
          return 1;
      }

    inode = statstruct.st_ino;

    chdir(".."); //go to the parent directory

    while (inode != 2) //when inode reaches 2, program stops
    {         
              dir = opendir(".");
              if (dir == NULL) //open parent directory
              {
                 perror("");
                 return 1;
              }

              structdirent=readdir(dir);

              int temp_inode = structdirent->d_ino;
              
              while (structdirent != NULL) 
              {
                  if (structdirent->d_ino == inode)
                  {
                    printf("%s\n", structdirent->d_name);
                  }
                  structdirent=readdir(dir);
              }

              inode = temp_inode;

              closedir(dir);

              chdir(".."); //repeat
    }



    printf("[root]\n");
    
    return 0;
}