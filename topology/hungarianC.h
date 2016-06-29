//TSTOP
//
//This program is free software: you can redistribute it and/or modify
//it under the terms of the GNU General Public License as published by
//the Free Software Foundation, either version 3 of the License, or
//(at your option) any later version.
//
//This program is distributed in the hope that it will be useful,
//but WITHOUT ANY WARRANTY; without even the implied warranty of
//MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//GNU General Public License for more details.
//
//You should have received a copy of the GNU General Public License
//along with this program.  If not, see <http://www.gnu.org/licenses/>.



//
//(Minimum) Assignment Problem by Hungarian Algorithm
//taken from Knuth's Stanford Graphbase
//
#ifndef HUNGARIAN_C
#define HUNGARIAN_C 1
#include <stdio.h>
#include <stdlib.h>

#define INF (0x7FFFFFFF)


int hungarian( int** Array , char** Result, int size1, int size2 )
{
int i,j;


unsigned int m=size1,n=size2;
int k;
int l;
int s;
int* col_mate = new int[size1];for ( int i = 0 ; i != size1 ; ++i )col_mate[i] = 0;
int* row_mate = new int[size2];for ( int i = 0 ; i != size2 ; ++i )row_mate[i] = 0;
int* parent_row = new int[size2];for ( int i = 0 ; i != size2 ; ++i )parent_row[i] = 0;
int* unchosen_row = new int[size1]; for ( int i = 0  ; i != size1 ; ++i )unchosen_row[i] = 0;
int t;
int q;
int* row_dec = new int[size1]; for ( int i = 0 ; i != size1 ; ++i )row_dec[i] = 0;
int* col_inc = new int[size2]; for ( int i = 0 ; i != size2 ; ++i )col_inc[i] = 0;
int* slack = new int[size2];for ( int i = 0 ; i != size2 ; ++i )slack[i] = 0;
int* slack_row = new int[size2];for ( int i = 0 ; i != size2 ; ++i )slack_row[i] = 0;
int unmatched;
int cost=0;

for (i=0;i<size1;++i)
  for (j=0;j<size2;++j)
    Result[i][j]=0;

// Begin subtract column minima in order to start with lots of zeroes 12

for (l=0;l<n;l++)
{
  s=Array[0][l];
  for (k=1;k<n;k++)
    if (Array[k][l]<s)
      s=Array[k][l];
  cost+=s;
  if (s!=0)
    for (k=0;k<n;k++)
      Array[k][l]-=s;
}
// End subtract column minima in order to start with lots of zeroes 12

// Begin initial state 16
t=0;
for (l=0;l<n;l++)
{
  row_mate[l]= -1;
  parent_row[l]= -1;
  col_inc[l]=0;
  slack[l]=INF;
}
for (k=0;k<m;k++)
{
  s=Array[k][0];
  for (l=1;l<n;l++)
    if (Array[k][l]<s)
      s=Array[k][l];
  row_dec[k]=s;
  for (l=0;l<n;l++)
    if (s==Array[k][l] && row_mate[l]<0)
    {
      col_mate[k]=l;
      row_mate[l]=k;

      goto row_done;
    }
  col_mate[k]= -1;

  unchosen_row[t++]=k;
row_done:
  ;
}
// End initial state 16

// Begin Hungarian algorithm 18
if (t==0)
  goto done;
unmatched=t;
while (1)
{

  q=0;
  while (1)
  {
    while (q<t)
    {
      // Begin explore node q of the forest 19
      {
        k=unchosen_row[q];
        s=row_dec[k];
        for (l=0;l<n;l++)
          if (slack[l])
          {
            int del;
            del=Array[k][l]-s+col_inc[l];
            if (del<slack[l])
            {
              if (del==0)
              {
                if (row_mate[l]<0)
                  goto breakthru;
                slack[l]=0;
                parent_row[l]=k;


                unchosen_row[t++]=row_mate[l];
              }
              else
              {
                slack[l]=del;
                slack_row[l]=k;
              }
          }
        }
      }
      // End explore node q of the forest 19
      q++;
    }

    // Begin introduce a new zero into the matrix 21
    s=INF;
    for (l=0;l<n;l++)
      if (slack[l] && slack[l]<s)
        s=slack[l];
    for (q=0;q<t;q++)
      row_dec[unchosen_row[q]]+=s;
    for (l=0;l<n;l++)
      if (slack[l])
      {
        slack[l]-=s;
        if (slack[l]==0)
        {
          // Begin look at a new zero 22
          k=slack_row[l];

          if (row_mate[l]<0)
          {
            for (j=l+1;j<n;j++)
              if (slack[j]==0)
                col_inc[j]+=s;
            goto breakthru;
          }
          else
          {
            parent_row[l]=k;

            unchosen_row[t++]=row_mate[l];
          }
          // End look at a new zero 22
        }
      }
      else
        col_inc[l]+=s;
    // End introduce a new zero into the matrix 21
  }
breakthru:
  // Begin update the matching 20

  while (1)
  {
    j=col_mate[k];
    col_mate[k]=l;
    row_mate[l]=k;

    if (j<0)
      break;
    k=parent_row[j];
    l=j;
  }
  // End update the matching 20
  if (--unmatched==0)
    goto done;
  // Begin get ready for another stage 17
  t=0;
  for (l=0;l<n;l++)
  {
    parent_row[l]= -1;
    slack[l]=INF;
  }
  for (k=0;k<m;k++)
    if (col_mate[k]<0)
    {

      unchosen_row[t++]=k;
    }
  // End get ready for another stage 17
}
done:

// Begin doublecheck the solution 23
for (k=0;k<m;k++)
  for (l=0;l<n;l++)
    if (Array[k][l]<row_dec[k]-col_inc[l])
      exit(0);
for (k=0;k<m;k++)
{
  l=col_mate[k];
  if (l<0 || Array[k][l]!=row_dec[k]-col_inc[l])
    exit(0);
}
k=0;
for (l=0;l<n;l++)
  if (col_inc[l])
    k++;
if (k>m)
  exit(0);
// End doublecheck the solution 23
// End Hungarian algorithm 18

for (i=0;i<m;++i)
{
  Result[i][col_mate[i]]=1;
 /*TRACE("%d - %d\n", i, col_mate[i]);*/
}
for (k=0;k<m;++k)
{
  for (l=0;l<n;++l)
  {
    /*TRACE("%d ",Array[k][l]-row_dec[k]+col_inc[l]);*/
    Array[k][l]=Array[k][l]-row_dec[k]+col_inc[l];
  }
  /*TRACE("\n");*/
}
for (i=0;i<m;i++)
  cost+=row_dec[i];
for (i=0;i<n;i++)
  cost-=col_inc[i];
return cost;
}
/*

main()
{
int y,x,i;

initArray();
//
for (y=0;y<size1;++y)
  for (x=0;x<size2;++x)
    Array[y][x]=abs(size1*x-y);
//
hungarian();


}
*/
#endif
