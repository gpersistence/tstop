#ifndef HUNGARIAN_DISTANCE_H
#define HUNGARIAN_DISTANCE_H

#include<cstring>
#include<algorithm>
#include<iostream>

#define HUNG_INF 1e9


/*
 * This is the Hungarian Distacen O(N3) bipartite matching algorithm
 * Partially taken from TopCoder excerpts and Wikipedia
 */
class HungarianDistance {

   public:


   /*
    * Assumes the costs are all  >= 0
    */
   HungarianDistance(double** _cost, int _n, bool _computeMinimum = false);
   ~HungarianDistance();


   /*
    * Default solves for the maximum-weighted matching, 
    * See _computeMinimum
    */
   double compute();

   /*
    * Returns the list of vertices st xy[x], is the vertex that is matched with x
    */
   void getMatches(int* _xy);

   private:

	int num_augment;
   void init();
   void initLabels();
   void augment();
   void update_labels();
   void addToTree(int _x, int _prevx);
   



   //Data//
   
   double** cost;          //cost matrix
   int n, max_match;    //n workers and n jobs
   double *lx, *ly;         //labels of X and Y parts
   int *xy;             //xy[x] - vertex that is matched with x,
   int *yx;             //yx[y] - vertex that is matched with y
   bool *S, *T;         //sets S and T in algorithm
   double *slack;          //as in the algorithm description
   int *slackx;         //slackx[y] such a vertex, that
                        // l(slackx[y]) + l(y) - w(slackx[y],y) = slack[y]
   int *prev;           //array for memorizing alternating paths

};

#endif
