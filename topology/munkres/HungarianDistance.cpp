#include "HungarianDistance.h"
#include<cstdio>
#include<cmath>

HungarianDistance::HungarianDistance(double** _cost, int _n, bool _computeMinimum) {

   n = _n;
	num_augment = 0;
  
   cost = new double*[n];

   //negate weights if minimum
   for(int i=0; i < n; i++) {
      cost[i] = new double[n];
      for(int j=0; j < n; j++) {
         cost[i][j] = _cost[i][j];
         if(_computeMinimum)  cost[i][j]  = -cost[i][j]; 
      }
   }
   max_match = 0;

   init();
}

HungarianDistance::~HungarianDistance() {
   delete[] lx;
   delete[] ly;

   delete[] xy;
   delete[] yx;
   
   delete[] S;
   delete[] T;

   delete[] slack;
   delete[] slackx;

   delete[] prev;

   for(int i=0; i < n; i++)
      delete [] cost[i];
	delete [] cost;
}

void HungarianDistance::init() {
   lx = new double[n];
   ly = new double[n];

   xy = new int[n];
   yx = new int[n];

   S  = new bool[n];
   T  = new bool[n];

   slack    = new double[n];
   slackx   = new int[n];

   prev = new int[n];
}

double HungarianDistance::compute() {

   double ret = 0;                   //weight of the optimal matching

   max_match = 0;                    //number of vertices in current matching
   std::fill(xy, xy+n, -1);
   std::fill(yx, yx+n, -1);

   initLabels();                    //step 0

   augment();                        //steps 1-3
   for (int x = 0; x < n; x++) {     //forming answer there
      ret += cost[x][xy[x]];
   }
   return fabs(ret); 
}


/*
 * Returns the list of vertices st xy[x], is the vertex that is matched with x
 */
void HungarianDistance::getMatches(int* _xy) {
   std::copy(xy, xy+n, _xy);
}



void HungarianDistance::initLabels() {
   std::fill(lx, lx+n, 0);
   std::fill(ly, ly+n, 0);
   for (int x = 0; x < n; x++) {
      for (int y = 0; y < n; y++) {
         lx[x] = std::max(lx[x], cost[x][y]);
      }
   }
}

void HungarianDistance::augment() {                       

   if (max_match == n) return;         //check wether matching is already perfect

   int x=0; int y=0; int root=0;       //just counters and root vertex
   int q[n], wr = 0, rd = 0;           //q - queue for bfs, wr,rd - write and read
                                       //pos in queue
   std::fill(S, S+n, false);
   std::fill(T, T+n, false);
   std::fill(prev, prev+n, -1);

   for (x = 0; x < n; x++) {           //finding root of the tree
      if (xy[x] == -1) {
         q[wr++] = root = x;
         prev[x] = -2;
         S[x] = true;
         break;
      }
   }

   for (y = 0; y < n; y++) {           //initializing slack array
      slack[y] = lx[root] + ly[y] - cost[root][y];
      slackx[y] = root;
   }

	num_augment++;
	std::cout << "entering main augment loop: " << num_augment << std::endl;
   //second part of augment() function
   while (true) {                                                        //main cycle
      while (rd < wr)                                                 //building tree with bfs cycle
      {
         x = q[rd++];                                                //current vertex from X part
         for (y = 0; y < n; y++)                                     //iterate through all edges in equality graph
            if (cost[x][y] == lx[x] + ly[y] &&  !T[y])
            {
               if (yx[y] == -1) break;                             //an exposed vertex in Y found, so
                                                                        //augmenting path exists!
               T[y] = true;                                        //else just add y to T,
               q[wr++] = yx[y];                                    //add vertex yx[y], which is matched
                                                                  //with y, to the queue
               addToTree(yx[y], x);                              //add edges (x,y) and (y,yx[y]) to the tree
            }
         if (y < n) break;                                           //augmenting path found!
      }
      if (y < n) break;                                               //augmenting path found!
      update_labels();                                                //augmenting path not found, so improve labeling
      wr = rd = 0;                
      for (y = 0; y < n; y++)        
         //in this cycle we add edges that were added to the equality graph as a
         //result of improving the labeling, we add edge (slackx[y], y) to the tree if
         //and only if !T[y] &&  slack[y] == 0, also with this edge we add another one
         //(y, yx[y]) or augment the matching, if y was exposed
         if (!T[y] &&  slack[y] == 0)
         {
            if (yx[y] == -1)                                        //exposed vertex in Y found - augmenting path exists!
            {
               x = slackx[y];
               break;
            }
            else
            {
               T[y] = true;                                        //else just add y to T,
               if (!S[yx[y]])    
               {
                  q[wr++] = yx[y];                                //add vertex yx[y], which is matched with
                                                                  //y, to the queue
                  addToTree(yx[y], slackx[y]);                  //and add edges (x,y) and (y,
                                                                        //yx[y]) to the tree
               }
            }
         }
      if (y < n) break;                                               //augmenting path found!
   }

   if (y < n)                                                          //we found augmenting path!
   {
      max_match++;                                                    //increment matching
      //in this cycle we inverse edges along augmenting path
      for (int cx = x, cy = y, ty; cx != -2; cx = prev[cx], cy = ty)
      {
         ty = xy[cx];
         yx[cy] = cx;
         xy[cx] = cy;
      }
      augment();                                                      //recall function, go to step 1 of the algorithm
   }
}//end of augment() function

void HungarianDistance::update_labels() {
   int x, y;
	double delta = HUNG_INF;             //init delta as infinity
   for (y = 0; y < n; y++)            //calculate delta using slack
      if (!T[y])
         delta = std::min(delta, slack[y]);
   for (x = 0; x < n; x++)            //update X labels
      if (S[x]) lx[x] -= delta;
   for (y = 0; y < n; y++)            //update Y labels
      if (T[y]) ly[y] += delta;
   for (y = 0; y < n; y++)            //update slack array
      if (!T[y])
         slack[y] -= delta;
}

void HungarianDistance::addToTree(int x, int prevx) {
//x - current vertex,prevx - vertex from X before x in the alternating path,
//so we add edges (prevx, xy[x]), (xy[x], x)

   S[x] = true;                    //add x to S
   prev[x] = prevx;                //we need this when augmenting
   for (int y = 0; y < n; y++) {   //update slacks, because we add new vertex to S
      if (lx[x] + ly[y] - cost[x][y] < slack[y]) {
         slack[y] = lx[x] + ly[y] - cost[x][y];
         slackx[y] = x;
      }
   }
}
