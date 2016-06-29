/*
    Copyrigth 2015, D. Morozov, M. Kerber, A. Nigmetov

    This file is part of GeomBottleneck.

    GeomBottleneck is free software: you can redistribute it and/or modify
    it under the terms of the Lesser GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    GeomBottleneck is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Lesser GNU General Public License for more details.

    You should have received a copy of the Lesser GNU General Public License
    along with GeomBottleneck.  If not, see <http://www.gnu.org/licenses/>.

*/


#include <algorithm>
#include "neighb_oracle.h"
#include "def_debug.h"

namespace geom_bt {
/*static void printDebug(//bool isDebug, std::string s)*/
//{
//#ifdef DEBUG_NEIGHBOUR_ORACLE
    //if (isDebug) {
        //std::cout << s << std::endl;
    //}
//#endif
//}

//static void printDebug(//bool isDebug, std::string s, const DiagramPoint& p)
//{
//#ifdef DEBUG_NEIGHBOUR_ORACLE
    //if (isDebug) {
        //std::cout << s << p << std::endl;
    //}
//#endif
//}

//static void printDebug(//bool isDebug, std::string s, const double r)
//{
//#ifdef DEBUG_NEIGHBOUR_ORACLE
    //if (isDebug) {
        //std::cout << s << r << std::endl;
    //}
//#endif
//}

//static void printDebug(//bool isDebug, std::string s, const DiagramPointSet& dpSet)
//{
//#ifdef DEBUG_NEIGHBOUR_ORACLE
    //if (isDebug) {
        //std::cout << s << dpSet << std::endl;
    //}
//#endif
//}



// simple oracle
NeighbOracleSimple::NeighbOracleSimple() 
{
    r  = 0.0;
}

NeighbOracleSimple::NeighbOracleSimple(const DiagramPointSet& S, const double rr, const double dEps)
{
    r = rr;
    distEpsilon = dEps;
    pointSet = S;
}

void NeighbOracleSimple::rebuild(const DiagramPointSet& S, const double rr)
{
    pointSet = S;
    r = rr;
}

void NeighbOracleSimple::deletePoint(const DiagramPoint& p)
{
    pointSet.erase(p);
}

bool NeighbOracleSimple::getNeighbour(const DiagramPoint& q, DiagramPoint& result) const
{
    for(auto pit = pointSet.cbegin(); pit != pointSet.cend(); ++pit) {
        if ( distLInf(*pit, q) <= r) {
            result = *pit;
            return true;
        }
    }
    return false;
}

void NeighbOracleSimple::getAllNeighbours(const DiagramPoint& q, std::vector<DiagramPoint>& result)
{
    result.clear();
    for(const auto& point : pointSet) {
        if ( distLInf(point, q) <= r) {
            result.push_back(point);
        }
    }
    for(auto& pt : result) {
        deletePoint(pt);
    }
}

// ANN oracle
//

NeighbOracleAnn::NeighbOracleAnn(const DiagramPointSet& S, const double rr, const double dEps)
{
    assert(dEps >= 0);
    distEpsilon = dEps;
    // allocate space for query point
    // and the output of nearest neighbour search
    // this memory will be used in getNeighbour and freed in destructor
    annQueryPoint = annAllocPt(annDim);
    annIndices = new ANNidx[annK];
    annDistances = new ANNdist[annK];
    annPoints = nullptr;
    lo = annAllocPt(annDim);
    hi = annAllocPt(annDim);
    // create kd tree
    kdTree = nullptr;
    rebuild(S, rr);
}

void NeighbOracleAnn::rebuild(const DiagramPointSet& S, double rr)
{
    //bool isDebug { false };
    //printDebug(isDebug, "Entered rebuild, r = ", rr);
    r = rr;
    size_t annNumPoints = S.size();
    //printDebug(isDebug, "S = ", S);
    if (annNumPoints  > 0) {
        //originalPointSet = S;
        pointIdxLookup.clear();
        pointIdxLookup.reserve(S.size());
        allPoints.clear();
        allPoints.reserve(S.size());
        diagonalPoints.clear();
        diagonalPoints.reserve(S.size() / 2);
        for(auto pit = S.cbegin(); pit != S.cend(); ++pit) {
            allPoints.push_back(*pit);
            if (pit->type == DiagramPoint::DIAG) {
                diagonalPoints.insert(*pit);
            }
        }
        if (annPoints) {
            annDeallocPts(annPoints);
        }
        annPoints = annAllocPts(annNumPoints, annDim);
        auto annPointsPtr = *annPoints;
        size_t pointIdx = 0;
        for(auto& dataPoint : allPoints) {
            pointIdxLookup.insert( { dataPoint, pointIdx++ } );
            *annPointsPtr++ = dataPoint.getRealX();
            *annPointsPtr++ = dataPoint.getRealY();
        }
        delete kdTree;
        kdTree = new ANNkd_tree(annPoints,
                                annNumPoints,
                                annDim,
                                1,                // bucket size
                                ANN_KD_STD);
    }
}

void NeighbOracleAnn::deletePoint(const DiagramPoint& p)
{
    //bool isDebug { true };
    auto findRes = pointIdxLookup.find(p);
    assert(findRes != pointIdxLookup.end());
    //printDebug(isDebug, "Deleting point ", p);
    size_t pointIdx { (*findRes).second };
    //printDebug(isDebug, "pointIdx =  ", pointIdx);
    //originalPointSet.erase(p);
    diagonalPoints.erase(p, false);
    kdTree->delete_point(pointIdx);
#ifdef DEBUG_NEIGHBOUR_ORACLE
    kdTree->Print(ANNtrue, std::cout);
#endif
}

bool NeighbOracleAnn::getNeighbour(const DiagramPoint& q, DiagramPoint& result) const
{
    //bool isDebug { false };
    //printDebug(isDebug, "getNeighbour for q = ", q);
    if (0 == kdTree->getActualNumPoints() ) {
        //printDebug(isDebug, "annNumPoints = 0, not found ");
        return false;
    }
    // distance between two diagonal points
    // is  0
    if (DiagramPoint::DIAG == q.type) {
        if (!diagonalPoints.empty()) {
            result = *diagonalPoints.cbegin();
            //printDebug(isDebug, "Neighbour found in diagonal points, res =  ", result);
            return true;
        }
    }
    // if no neighbour found among diagonal points, 
    // search in ANN kd_tree
    annQueryPoint[0] = q.getRealX();
    annQueryPoint[1] = q.getRealY();
    //annIndices[0] = ANN_NULL_IDX;
    kdTree->annkSearch(annQueryPoint, annK, annIndices, annDistances, annEpsilon);
    //kdTree->annkFRSearch(annQueryPoint, r, annK, annIndices, annDistances, annEpsilon);
    //std::cout << distEpsilon << " = distEpsilon " << std::endl;
    if (annDistances[0] <= r + distEpsilon) {
    //if (annIndices[0] != ANN_NULL_IDX) {
        result = allPoints[annIndices[0]];
        //printDebug(isDebug, "Neighbour found with kd-tree, index =  ", annIndices[0]);
        //printDebug(isDebug, "result =  ", result);
        return true;
    }
    //printDebug(isDebug, "No neighbour found for r =  ", r);
    return false;
}

void NeighbOracleAnn::getAllNeighbours(const DiagramPoint& q, std::vector<DiagramPoint>& result)
{
    //bool isDebug { true };
    //printDebug(isDebug, "Entered getAllNeighbours for q = ", q);
    result.clear();
    // add diagonal points, if necessary
    if ( DiagramPoint::DIAG == q.type) { 
        for( auto& diagPt : diagonalPoints ) {
            result.push_back(diagPt);
        }
    }
    // delete diagonal points we found
    // to prevent finding them again
    for(auto& pt : result) {
        //printDebug(isDebug, "deleting DIAG point pt = ", pt);
        deletePoint(pt);
    }
    size_t diagOffset = result.size();
    // create the query rectangle
    // centered at q of radius r
    lo[0] = q.getRealX() - r;
    lo[1] = q.getRealY() - r;
    hi[0] = q.getRealX() + r;
    hi[1] = q.getRealY() + r;
    ANNorthRect annRect { annDim, lo, hi };
    std::vector<size_t> pointIndicesOut;
    // perorm range search on kd-tree
    kdTree->range_search(annRect, pointIndicesOut);
    // get actual points in result
    for(auto& ptIdx : pointIndicesOut) {
        result.push_back(allPoints[ptIdx]);
    }
    // delete all points we found
    for(auto ptIt = result.begin() + diagOffset; ptIt != result.end(); ++ptIt) {
        //printDebug(isDebug, "deleting point pt = ", *ptIt);
        deletePoint(*ptIt);
    }
}

NeighbOracleAnn::~NeighbOracleAnn()
{
    delete [] annIndices;
    delete [] annDistances;
    delete kdTree;
    annDeallocPt(annQueryPoint);
    annDeallocPt(lo);
    annDeallocPt(hi);
    if (annPoints) {
        annDeallocPts(annPoints);
    }
}
}
