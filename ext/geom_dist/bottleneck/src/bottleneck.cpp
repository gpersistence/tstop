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


#include <iomanip>
#include <sstream>
#include <string>
#include <cctype>

#include "bottleneck.h"
//#include "test_dist_calc.h"

namespace geom_bt {

// return the interval (distMin, distMax) such that: 
// a) actual bottleneck distance between A and B is contained in the interval
// b) if the interval is not (0,0), then  (distMax - distMin) / distMin < epsilon 
std::pair<double, double> bottleneckDistApproxInterval(DiagramPointSet& A, DiagramPointSet& B, const double epsilon)
{
    // empty diagrams are not considered as error
    if (A.empty() and B.empty())
        return std::make_pair(0.0, 0.0);

    // link diagrams A and B by adding projections
    addProjections(A, B);

    // TODO: think about that!
    // we need one threshold for checking if the distance is 0,
    // another one for the oracle!
    constexpr double epsThreshold { 1.0e-10 };
    std::pair<double, double> result { 0.0, 0.0 };
    bool useRangeSearch { true };
    // construct an oracle
    BoundMatchOracle oracle(A, B, epsThreshold, useRangeSearch);
    // check for distance = 0
    if (oracle.isMatchLess(2*epsThreshold)) {
        return result;
    }
    // get a 3-approximation of maximal distance between A and B
    // as a starting value for probe distance
    double distProbe  { getFurthestDistance3Approx(A, B) };
    // aliases for result components
    double& distMin {result.first};
    double& distMax {result.second};

    if ( oracle.isMatchLess(distProbe) ) {
        // distProbe is an upper bound, 
        // find lower bound with binary search
        do {
            distMax = distProbe;
            distProbe /= 2.0;
        } while (oracle.isMatchLess(distProbe));
        distMin = distProbe;
    } else {
        // distProbe is a lower bound,
        // find upper bound with exponential search
        do {
            distMin = distProbe;
            distProbe *= 2.0;
        } while (!oracle.isMatchLess(distProbe));
        distMax = distProbe;
    }
    // bounds are found, perform binary search
    //std::cout << "Bounds found, distMin = " << distMin << ", distMax = " << distMax << ", ratio = " << ( distMax - distMin ) / distMin << std::endl ;
    distProbe = ( distMin + distMax ) / 2.0;
    while (  ( distMax - distMin ) / distMin >= epsilon ) {
        if (oracle.isMatchLess(distProbe)) {
            distMax = distProbe;
        } else {
            distMin = distProbe;
        }
        distProbe = ( distMin + distMax ) / 2.0;
    }
    return result;
}

// get approximate distance,
// see bottleneckDistApproxInterval
double bottleneckDistApprox(DiagramPointSet& A, DiagramPointSet& B, const double epsilon)
{
    auto interval = bottleneckDistApproxInterval(A, B, epsilon);
    return interval.second;
}


double bottleneckDistExactFromSortedPwDist(DiagramPointSet&A, DiagramPointSet& B, std::vector<double>& pairwiseDist)
{
    //for(size_t k = 0; k < pairwiseDist.size(); ++k) {
        //std::cout << "pairwiseDist[" << k << "] = " << std::setprecision(15) << pairwiseDist[k] << std::endl;
    //}
    // trivial case: we have only one candidate
    if (pairwiseDist.size() == 1) 
        return pairwiseDist[0];

    bool useRangeSearch = true;
    double distEpsilon = std::numeric_limits<double>::max();
    for(size_t k = 0; k < pairwiseDist.size() - 2; ++k) {
        auto diff = pairwiseDist[k+1]- pairwiseDist[k];
        if ( diff > 1.0e-14 and diff < distEpsilon ) {
            distEpsilon = diff;
        }
    }
    distEpsilon /= 3.0;

    BoundMatchOracle oracle(A, B, distEpsilon, useRangeSearch);
    // binary search
    size_t iterNum {0};
    size_t idxMin {0}, idxMax {pairwiseDist.size() - 1};
    size_t idxMid;
    while(idxMax > idxMin) {
        idxMid = static_cast<size_t>(floor(idxMin + idxMax) / 2.0);
        //std::cout << "while begin: min = " << idxMin << ", idxMax = " << idxMax << ", idxMid = " << idxMid << ", testing d = " << std::setprecision(15) << pairwiseDist[idxMid] << std::endl;
        iterNum++;
        // not A[imid] < dist <=>  A[imid] >= dist  <=> A[imid[ >= dist + eps
        if (oracle.isMatchLess(pairwiseDist[idxMid] + distEpsilon / 2.0)) {
            //std::cout << "isMatchLess = true" << std::endl;
            idxMax = idxMid;
        } else {
            //std::cout << "isMatchLess = false " << std::endl;
            idxMin = idxMid + 1;
        }
        //std::cout << "while end: idxMin = " << idxMin << ", idxMax = " << idxMax << ", idxMid = " << idxMid << std::endl;
    }
    idxMid = static_cast<size_t>(floor(idxMin + idxMax) / 2.0);
    return pairwiseDist[idxMid];
}


double bottleneckDistExact(DiagramPointSet& A, DiagramPointSet& B)
{
    constexpr double epsilon = 0.001;
    auto interval = bottleneckDistApproxInterval(A, B, epsilon);
    const double delta = 0.5 * (interval.second - interval.first);
    const double approxDist = 0.5 * ( interval.first + interval.second);
    const double minDist = interval.first;
    const double maxDist = interval.second;
    //std::cerr << std::setprecision(15) <<  "minDist = " << minDist << ", maxDist = " << maxDist << std::endl;
    if ( delta == 0 ) {
        return interval.first;
    }
    // copy points from A to a vector
    // todo: get rid of this?
    std::vector<DiagramPoint> pointsA;
    pointsA.reserve(A.size());
    for(const auto& ptA : A) {
        pointsA.push_back(ptA);
    }

    //std::vector<double> killDist;
    //for(auto ptA : A) {
        //for(auto ptB : B) {
            //if ( distLInf(ptA, ptB) > minDist and distLInf(ptA, ptB) < maxDist) {
                //killDist.push_back(distLInf(ptA, ptB));
                //std::cout << ptA << ", " << ptB << std::endl;
            //}
        //}
    //}
    //std::sort(killDist.begin(), killDist.end());
    //for(auto d : killDist) {
        //std::cout << d << std::endl;
    //}
    //std::cout << "*************" << std::endl;

    // in this vector we store the distances between the points
    // that are candidates to realize 
    std::vector<double> pairwiseDist;
    {
        // vector to store centers of vertical stripes
        // two for each point in A and the id of the corresponding point
        std::vector<std::pair<double, DiagramPoint>> xCentersVec;
        xCentersVec.reserve(2 * pointsA.size());
        for(auto ptA : pointsA) {
            xCentersVec.push_back(std::make_pair(ptA.getRealX() - approxDist, ptA));
            xCentersVec.push_back(std::make_pair(ptA.getRealX() + approxDist, ptA));
        }
        // lambda to compare pairs <coordinate, id> w.r.t coordinate
        auto compLambda = [](std::pair<double, DiagramPoint> a, std::pair<double, DiagramPoint> b)
                                { return a.first < b.first; };
        
        std::sort(xCentersVec.begin(), xCentersVec.end(), compLambda);
        //std::cout << "xCentersVec.size  = " << xCentersVec.size() << std::endl;
        //for(auto p = xCentersVec.begin(); p!= xCentersVec.end(); ++p) {
            //if (p->second.id == 200) {
                //std::cout << "index of 200: " << p - xCentersVec.begin() << std::endl;
            //}
        //}
        //std::vector<DiagramPoint> 
        // todo: sort points in B, reduce search range in lower and upper bounds
        for(auto ptB : B) {
            // iterator to the first stripe such that ptB lies to the left
            // from its right boundary (x_B <= x_j + \delta iff x_j >= x_B - \delta
            auto itStart = std::lower_bound(xCentersVec.begin(),
                                            xCentersVec.end(), 
                                            std::make_pair(ptB.getRealX() - delta, ptB),
                                            compLambda);
            //if (ptB.id == 236) {
                //std::cout << itStart - xCentersVec.begin() <<  std::endl;
            //}

            for(auto iterA = itStart; iterA < xCentersVec.end(); ++iterA) {
                //if (ptB.id == 236) {
                    //std::cout << "consider " << iterA->second << std::endl;
                //}
                if ( ptB.getRealX() < iterA->first - delta) {
                    // from that moment x_B >= x_j - delta
                    // is violated: x_B no longer lies to right from the left
                    // boundary of current stripe
                    //if (ptB.id == 236) {
                        //std::cout << "break" << std::endl;
                    //}
                    break;
                }
                // we're here => ptB lies in vertical stripe,
                // check if distance fits into the interval we've found
                double pwDist = distLInf(iterA->second, ptB);
                //if (ptB.id == 236) {
                    //std::cout << pwDist << std::endl;
                //}
                //std::cout << 1000*minDist << " <= " << 1000*pwDist << " <= " << 1000*maxDist << std::endl;
                if (pwDist >= minDist and pwDist <= maxDist) {
                    pairwiseDist.push_back(pwDist);
                }
            }
        }
    }

    {
        // for y
        // vector to store centers of vertical stripes
        // two for each point in A and the id of the corresponding point
        std::vector<std::pair<double, DiagramPoint>> yCentersVec;
        yCentersVec.reserve(2 * pointsA.size());
        for(auto ptA : pointsA) {
            yCentersVec.push_back(std::make_pair(ptA.getRealY() - approxDist, ptA));
            yCentersVec.push_back(std::make_pair(ptA.getRealY() + approxDist, ptA));
        }
        // lambda to compare pairs <coordinate, id> w.r.t coordinate
        auto compLambda = [](std::pair<double, DiagramPoint> a, std::pair<double, DiagramPoint> b)
                                { return a.first < b.first; };
        
        std::sort(yCentersVec.begin(), yCentersVec.end(), compLambda);

        //  std::cout << "Sorted vector of y-centers:" << std::endl;
        //for(auto coordPtPair : yCentersVec) {
            //std::cout << coordPtPair.first << ", id = " << coordPtPair.second.id << std::endl;
        //}
        /*std::cout << "End of sorted vector of y-centers:" << std::endl;*/

        //std::vector<DiagramPoint> 
        // todo: sort points in B, reduce search range in lower and upper bounds
        for(auto ptB : B) {
            auto itStart = std::lower_bound(yCentersVec.begin(),
                                            yCentersVec.end(), 
                                            std::make_pair(ptB.getRealY() - delta, ptB),
                                            compLambda);

            //if (ptB.id == 316) {
                //std::cout << itStart - yCentersVec.begin() <<  " "  << distLInf(itStart->second, ptB) << std::endl;
                //std::cout << "maxDist = " << maxDist << std::endl;
                //std::cout << "minDist = " << minDist << std::endl;
                //double pwDistDebug = distLInf(itStart->second, ptB);
                //std::cout << ( pwDistDebug >= minDist and pwDistDebug <= maxDist) << std::endl;
            //}

            for(auto iterA = itStart; iterA < yCentersVec.end(); ++iterA) {
                if ( ptB.getRealY() < iterA->first - delta) {
                    break;
                }
                double pwDist = distLInf(iterA->second, ptB);
                //std::cout << 1000*minDist << " <= " << 1000*pwDist << " <= " << 1000*maxDist << std::endl;
                if (pwDist >= minDist and pwDist <= maxDist) {
                    //if (ptB.id == 316) {
                        //std::cout << "adding " << pwDist << std::endl;
                    //}
                    pairwiseDist.push_back(pwDist);
                }
            }
        }
    }

    //std::cerr << "pairwiseDist.size = " << pairwiseDist.size() << " out of " << A.size() * A.size() << std::endl;
    std::sort(pairwiseDist.begin(), pairwiseDist.end());
    //for(auto ddd : pairwiseDist) {
        //std::cerr << std::setprecision(15) << ddd << std::endl;
    //}

    return bottleneckDistExactFromSortedPwDist(A, B, pairwiseDist);
}

double bottleneckDistSlow(DiagramPointSet& A, DiagramPointSet& B)
{
    // use range search when building the layer graph
    bool useRangeSearch { true };
    // find maximum of min. distances for each point,
    // use this value as lower bound for bottleneck distance
    bool useHeurMinIdx { true };

    // find matching in a greedy manner to
    // get an upper bound for a bottleneck distance
    bool useHeurGreedyMatching { false };

    // use successive multiplication of idxMin with 2 to get idxMax
    bool goUpToFindIdxMax { false };
    // 
    goUpToFindIdxMax = goUpToFindIdxMax and !useHeurGreedyMatching; 

    if (!useHeurGreedyMatching) {
        long int N = 3 * (A.size() / 2 ) * (B.size() / 2);
        std::vector<double> pairwiseDist;
        pairwiseDist.reserve(N);
        double maxMinDist {0.0};
        for(auto& p_A : A) {
            double minDist { std::numeric_limits<double>::max() };
            for(auto& p_B : B) {
                if (p_A.type != DiagramPoint::DIAG or p_B.type != DiagramPoint::DIAG) {
                    double d = distLInf(p_A, p_B);
                    pairwiseDist.push_back(d);
                    if (useHeurMinIdx and p_A.type != DiagramPoint::DIAG) {
                        if (d < minDist)
                            minDist = d;
                    }
                }
            }
            if (useHeurMinIdx and DiagramPoint::DIAG != p_A.type and minDist > maxMinDist) {
                maxMinDist = minDist;
            }
        }
        std::sort(pairwiseDist.begin(), pairwiseDist.end());

        double distEpsilon = std::numeric_limits<double>::max();
        for(size_t k = 0; k < pairwiseDist.size() - 2; ++k) {
            auto diff = pairwiseDist[k+1]- pairwiseDist[k];
            if ( diff > 1.0e-10 and diff < distEpsilon ) {
                distEpsilon = diff;
            }
        }
        distEpsilon /= 3.0;

        BoundMatchOracle oracle(A, B, distEpsilon, useRangeSearch);
        // binary search
        size_t iterNum {0};
        size_t idxMin {0}, idxMax {pairwiseDist.size() - 1};
        if (useHeurMinIdx) {
            auto maxMinIter = std::equal_range(pairwiseDist.begin(), pairwiseDist.end(), maxMinDist);
            assert(maxMinIter.first != pairwiseDist.end());
            idxMin = maxMinIter.first - pairwiseDist.begin();
            //std::cout << "maxMinDist = " << maxMinDist << ", idxMin = " << idxMin << ", d = " << pairwiseDist[idxMin] << std::endl;
        }

        if (goUpToFindIdxMax) {
            if ( pairwiseDist.size() == 1) {
                return pairwiseDist[0];
            }

            idxMax = std::max<size_t>(idxMin, 1);
            while (!oracle.isMatchLess(pairwiseDist[idxMax])) {
                //std::cout << "entered while" << std::endl;
                idxMin = idxMax;
                if (2*idxMax > pairwiseDist.size() -1) {
                    idxMax = pairwiseDist.size() - 1;
                    break;
                } else {
                    idxMax *= 2;
                }
            }
            //std::cout << "size = " << pairwiseDist.size() << ", idxMax = " << idxMax <<  ", pw[max] = " << pairwiseDist[idxMax] << std::endl;
        }

        size_t idxMid { (idxMin + idxMax) / 2 };
        while(idxMax > idxMin) {
            iterNum++;
            if (oracle.isMatchLess(pairwiseDist[idxMid])) {
                idxMax = idxMid;
            } else {
                if (idxMax - idxMin == 1)
                    idxMin++;
                else
                    idxMin = idxMid;
            }
            idxMid = (idxMin + idxMax) / 2;
        }
        return pairwiseDist[idxMid];
    } else {
        // with greeedy matching
        long int N = A.size() * B.size();
        std::vector<DistVerticesPair> pairwiseDist;
        pairwiseDist.reserve(N);
        double maxMinDist {0.0};
        size_t idxA{0}, idxB{0};
        for(auto p_A : A) {
            double minDist { std::numeric_limits<double>::max() };
            idxB = 0;
            for(auto p_B : B) {
                double d = distLInf(p_A, p_B);
                pairwiseDist.push_back( std::make_pair(d, std::make_pair(idxA, idxB) ) );
                if (useHeurMinIdx and p_A.type != DiagramPoint::DIAG) {
                    if (d < minDist)
                        minDist = d;
                }
                idxB++;
            }
            if (useHeurMinIdx and DiagramPoint::DIAG != p_A.type and minDist > maxMinDist) {
                maxMinDist = minDist;
            }
            idxA++;
        }

        auto compLambda = [](DistVerticesPair a, DistVerticesPair b) 
                    { return a.first < b.first;};

        std::sort(pairwiseDist.begin(), 
                  pairwiseDist.end(), 
                  compLambda);

        double distEpsilon = std::numeric_limits<double>::max();
        for(size_t k = 0; k < pairwiseDist.size() - 2; ++k) {
            auto diff = pairwiseDist[k+1].first - pairwiseDist[k].first;
            if ( diff > 1.0e-10 and diff < distEpsilon ) {
                distEpsilon = diff;
            }
        }
        distEpsilon /= 3.0;

        BoundMatchOracle oracle(A, B, distEpsilon, useRangeSearch);

        // construct greedy matching
        size_t numVert { A.size() };
        size_t numMatched { 0 };
        std::unordered_set<size_t> aTobMatched, bToaMatched;
        aTobMatched.reserve(numVert);
        bToaMatched.reserve(numVert);
        size_t distVecIdx {0};
        while( numMatched < numVert) {
            auto vertPair = pairwiseDist[distVecIdx++].second;
            //std::cout << "distVecIdx = " << distVecIdx <<   ", matched: " << numMatched << " out of " << numVert << std::endl;
            //std::cout << "vertex A idx = " << vertPair.first <<   ", B idx: " << vertPair.second << " out of " << numVert << std::endl;
            if ( aTobMatched.count(vertPair.first) == 0 and
                 bToaMatched.count(vertPair.second) == 0 ) {
                aTobMatched.insert(vertPair.first);
                bToaMatched.insert(vertPair.second);
                numMatched++;
            }
        }
        size_t idxMax = distVecIdx-1;
        //std::cout << "idxMax = " << idxMax << ", size = " << pairwiseDist.size() << std::endl;
        // binary search
        size_t iterNum {0};
        size_t idxMin {0};
        if (useHeurMinIdx) {
            auto maxMinIter = std::equal_range(pairwiseDist.begin(),
                                               pairwiseDist.end(), 
                                               std::make_pair(maxMinDist, std::make_pair(0,0)),
                                               compLambda);
            assert(maxMinIter.first != pairwiseDist.end());
            idxMin = maxMinIter.first - pairwiseDist.begin();
            //std::cout << "maxMinDist = " << maxMinDist << ", idxMin = " << idxMin << ", d = " << pairwiseDist[idxMin].first << std::endl;
        }
        size_t idxMid { (idxMin + idxMax) / 2 };
        while(idxMax > idxMin) {
            iterNum++;
            if (oracle.isMatchLess(pairwiseDist[idxMid].first)) {
                idxMax = idxMid;
            } else {
                if (idxMax - idxMin == 1)
                    idxMin++;
                else
                    idxMin = idxMid;
            }
            idxMid = (idxMin + idxMax) / 2;
        }
        return pairwiseDist[idxMid].first;
    }
    // stats
    /*
    // count number of edges
    // pairwiseDist is sorted, add edges of the same length
    int edgeNumber {idxMid};
    while(pairwiseDist[edgeNumber + 1] == pairwiseDist[edgeNumber])
        edgeNumber++;
    // add edges between diagonal points
    edgeNumber += N / 3;
    // output stats
    std::cout << idxMid << "\t" << N;
    std::cout << "\t" << iterNum;
    std::cout << "\t" << A.size() + B.size();
    std::cout << "\t" << edgeNumber << "\t";
    std::cout << (double)(edgeNumber) / (double)(A.size() + B.size()) << std::endl;
    */
}

bool readDiagramPointSet(const std::string& fname, std::vector<std::pair<double, double>>& result)
{
    return readDiagramPointSet(fname.c_str(), result);
}

bool readDiagramPointSet(const char* fname, std::vector<std::pair<double, double>>& result)
{
    size_t lineNumber { 0 };
    result.clear();
    std::ifstream f(fname);
    if (!f.good()) {
        std::cerr << "Cannot open file " << fname << std::endl;
        return false;
    }
    std::string line;
    while(std::getline(f, line)) {
        lineNumber++;
        // process comments: remove everything after hash
        auto hashPos = line.find_first_of("#", 0);
        if( std::string::npos != hashPos) {
            line = std::string(line.begin(), line.begin() + hashPos);
        }
        if (line.empty()) {
            continue;
        }
         // trim whitespaces 
        auto whiteSpaceFront = std::find_if_not(line.begin(),line.end(),isspace);
        auto whiteSpaceBack = std::find_if_not(line.rbegin(),line.rend(),isspace).base();
        if (whiteSpaceBack <= whiteSpaceFront) {
            // line consists of spaces only - move to the next line
            continue;
        }
        line = std::string(whiteSpaceFront,whiteSpaceBack);
        double x, y;
        std::istringstream iss(line);
        if (not(iss >> x >> y)) {
            std::cerr << "Error in file " << fname << ", line number " << lineNumber << ": cannot parse \"" << line << "\"" << std::endl;
            return false;
        }
        result.push_back(std::make_pair(x,y));
    }
    f.close();
    return true;
}



}
