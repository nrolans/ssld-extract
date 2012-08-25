/*  main.c  */
/*  Copyright (C) 2012 Alex Kozadaev [akozadaev at yahoo com]  */

#include <stdio.h>
#include <string.h>
#include <ctype.h>

#include "conn.h"

#define VERSION "1.03"
#define MAX     2048

/* TODO: refactor the code(partially done). Its kinda ugly and written within a couple of hours. 
 * The reason for creating this is to compare python, perl and C implementations 
 * (perl uses regexp hence its the slowest version. Even in perl - regexp sucks) 
 */

static void parse(char *fname); /* main parsing logic */
static bool readline(FILE *in, char *str, int max); 
static void readvalues(char *line, bool iscn);  /* true = connection number, false = port */
static void usage(void);

/*=============================================================================*/
int
main(int argc, char **argv)
{
  char *fname = NULL;

  if (argc == 1) {
    usage();
    exit(1);
  }

  conn_init();
  atexit(conn_free);

  for (int i=1; i < argc; i++) { /* reading arguments */
    if (argv[i][0] == '-' && strlen(argv[i]) > 1) {
      switch(argv[i][1]) {
        case 'n': case 'p':
          readvalues(argv[i+1], argv[i][1] == 'n'); i++; break;
        case 'h':
          usage(); exit(0); 
        default:
          usage();
          fputs("ERROR: Invalid argument\n", stderr);
          exit(1);
      }
    } else 
      fname = argv[i];
  } /* reading arguments */

  parse(fname);
  return 0;
}

/*=============================================================================*/
static void
parse(char *fname)
{
  int cn, port;
  FILE *in;
  bool closable = false;
  bool inside = false;
  char line[MAX];

 
  if (fname && strlen(fname) == 1 && fname[0] == '-') 
    in = stdin;
  else {
    if ((in = fopen(fname, "r")) == NULL) {
      fputs("ERROR: input is not specified\n", stderr);
      exit(1);
    }
    closable = true;
  }

  while (readline(in, line, MAX)) {
    cn = port = 0;
    if (strncmp(line, "New", 3) == 0) {
      char *strp;
      for (strp = line; *strp != '#'; strp++)
        ;
      sscanf(strp, "#%d:", &cn); 

      for(; *(++strp) != '(';)
        ;
      sscanf(strp, "(%d)", &port);

      if(conn_exists(cn, port)) {
        puts(line);
        inside = true;
      }
    } else if (isdigit(line[0])) {
      sscanf(line, "%d", &cn);
      if (conn_exists(cn, -1)) {
        puts(line);
        inside = true;
      } else
        inside = false;
    } else if (isspace(line[0]) && inside) 
      puts(line);
  }
  if (closable)
    fclose(in);
}

/*=============================================================================*/
static bool
readline(FILE *in, char *str, int max)
{
  int i = 0;
  char ch;

  while ((ch = fgetc(in)) != EOF && ch != '\n') {
    if (i >= max) break;
    str[i++] = ch;
  }
  str[i] = '\0';
  return ch != EOF;
}

/*=============================================================================*/
static void
readvalues(char *line, bool iscn)
{
  int value;
  char *strp = line;

  if (!line) {
    puts("ERROR: argument is NULL");
    exit(1);
  }

  /* parsing comma separated parameters */
  while(true) {
    if (isdigit(strp[0])) {
      value = 0;
      if (sscanf(strp, "%d", &value) != EOF) {
        if (iscn)
          conn_addc(value);
        else
          conn_addp(value);
      }
      for (; *strp != ',' && *strp != '\0'; strp++)
        ;
      if (*strp == '\0') break;
      strp++;
    }
  }
}

/*=============================================================================*/
static void
usage(void)
{
  puts(
      "ssld-extract v" VERSION " Alex Kozadaev(C)                                   \n\n"
      "ssld-extact [-n x,y | -p n,m] [ssldump filename | - to read from pipe]       \n\n"
      "Extract one or more connections from a SSL dump file.                        \n\n"
      "    Usage:                                                                   \n"
      "        -n    comma separated list of connection numbers (no spaces allowed) \n"
      "        -p    comma separated list of client port numbers (no spaces allowed)\n"
      "        -h    this text                                                      \n\n");
}

/*  EOF:  main.c */
