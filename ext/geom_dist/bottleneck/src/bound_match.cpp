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

#include <iostream>
#include <assert.h>
#include "bound_match.h"

namespace geom_bt {
/*static void printDebug(//bool isDebug, std::string s)*/
//{
//#ifdef DEBUG_BOUND_MATCH
    //if (isDebug) {
        //std::cout << s << std::endl;
    //}
//#endif
//}

//static void printDebug(//bool isDebug, std::string s, const Matching& m)
//{
//#ifdef DEBUG_BOUND_MATCH
    //if (isDebug) {
        //std::cout << s << std::endl;
        //std::cout << m << std::endl;
    //}
//#endif
//}

//static void printDebug(//bool isDebug, std::string s, const DiagramPoint& p)
//{
//#ifdef DEBUG_BOUND_MATCH
    //if (isDebug) {
        //std::cout << s << p << std::endl;
    //}
//#endif
//}

//static void printDebug(//bool isDebug, std::string s, const double r)
//{
//#ifdef DEBUG_BOUND_MATCH
    //if (isDebug) {
        //std::cout << s << r << std::endl;
    //}
//#endif
//}

//static void printDebug(//bool isDebug, std::string s, const Path p)
//{
//#ifdef DEBUG_BOUND_MATCH
    //if (isDebug) {
        //std::cout << s;
        //for(auto pt : p) {
            //std::cout << pt << "; ";
        //}
        //std::cout << std::endl;
    //}
//#endif
//}

//static void printDebug(//bool isDebug, std::string s, const DiagramPointSet& dpSet)
//{
//#ifdef DEBUG_BOUND_MATCH
    //if (isDebug) {
        //std::cout << s << dpSet << std::endl;
    //}
//#endif
/*}*/

std::ostream& operator<<(std::ostream& output, const Matching& m)
{
    output << "Matching: " << m.AToB.size() << " pairs (";
    if (!m.isPerfect()) {
        output << "not";
    }
    output << " perfect)" << std::endl;
    for(auto atob : m.AToB) {
        output << atob.first << " <-> " << atob.second << "  distance: " << distLInf(atob.first, atob.second) << std::endl;
    }
    return output;
}

void Matching::sanityCheck() const
{
#ifdef DEBUG_MATCHING
    assert( AToB.size() == BToA.size() );
    for(auto aToBPair : AToB) {
        auto bToAPair = BToA.find(aToBPair.second);
        assert(bToAPair != BToA.end());
        if (aToBPair.first != bToAPair->second) {
            std::cerr << "failed assertion, in aToB " << aToBPair.first;
            std::cerr << ", in bToA " << bToAPair->second << std::endl;
        }
        assert( aToBPair.first == bToAPair->second);
    }
#endif 
}

bool Matching::isPerfect() const
{
    //sanityCheck();
    return AToB.size() == A.size();
}

void Matching::matchVertices(const DiagramPoint& pA, const DiagramPoint& pB)
{
    assert(A.hasElement(pA));
    assert(B.hasElement(pB));
    AToB.erase(pA);
    AToB.insert( {{ pA, pB }} );
    BToA.erase(pB);
    BToA.insert( {{ pB, pA }} );
}

bool Matching::getMatchedVertex(const DiagramPoint& p, DiagramPoint& result) const
{
    sanityCheck();
    auto inA = AToB.find(p);
    if (inA != AToB.end()) {
        result = (*inA).second;
        return true;
    } else {
        auto inB = BToA.find(p);
        if (inB != BToA.end()) {
            result = (*inB).second;
            return true;
        }
    }
    return false;
}


void Matching::checkAugPath(const Path& augPath) const
{
    assert(augPath.size() % 2 == 0);
    for(size_t idx = 0; idx < augPath.size(); ++idx) {
        bool mustBeExposed  { idx == 0 or idx == augPath.size() - 1 };
        if (isExposed(augPath[idx]) != mustBeExposed) {
            std::cerr << "mustBeExposed = " << mustBeExposed << ", idx = " << idx << ", point " << augPath[idx] << std::endl;
        }
        assert( isExposed(augPath[idx]) == mustBeExposed );
        DiagramPoint matchedVertex {0.0, 0.0, DiagramPoint::DIAG, 1};
        if ( idx % 2 == 0 ) {
            assert( A.hasElement(augPath[idx]));
            if (!mustBeExposed) {
                getMatchedVertex(augPath[idx], matchedVertex);
                assert(matchedVertex == augPath[idx - 1]);
            }
        } else {
            assert( B.hasElement(augPath[idx]));
            if (!mustBeExposed) {
                getMatchedVertex(augPath[idx], matchedVertex);
                assert(matchedVertex == augPath[idx + 1]);
            }
        }
    }
}

// use augmenting path to increase
// the size of the matching
void Matching::increase(const Path& augPath)
{
    //bool isDebug {false};
    sanityCheck();
    // check that augPath is an augmenting path
    checkAugPath(augPath);
    for(size_t idx = 0; idx < augPath.size() - 1; idx += 2) {
        matchVertices( augPath[idx], augPath[idx + 1]);
    }
    //printDebug(isDebug, "", *this);
    sanityCheck();
}

DiagramPointSet Matching::getExposedVertices(bool forA) const
{
    sanityCheck();
    DiagramPointSet result;
    const DiagramPointSet* setToSearch { forA ? &A : &B };
    const std::unordered_map<DiagramPoint, DiagramPoint, DiagramPointHash>* mapToSearch { forA ? &AToB : &BToA };
    for(auto it = setToSearch->cbegin(); it != setToSearch->cend(); ++it) {
        if (mapToSearch->find((*it)) == mapToSearch->cend()) {
            result.insert((*it));
        }
    }
    return result;
}

void Matching::getAllAdjacentVertices(const DiagramPointSet& setIn, 
                                      DiagramPointSet& setOut,
                                      bool forA) const
{
    sanityCheck();
    //bool isDebug {false};
    setOut.clear();
    const std::unordered_map<DiagramPoint, DiagramPoint, DiagramPointHash>* m;
    m = ( forA ) ? &BToA : &AToB;
    for(auto pit = setIn.cbegin(); pit != setIn.cend(); ++pit) {
        auto findRes = m->find(*pit);
        if (findRes != m->cend()) {
            setOut.insert((*findRes).second);
        }
    }
    //printDebug(isDebug, "got all adjacent vertices for ", setIn);
    //printDebug(isDebug, "the result is: ", setOut);
    sanityCheck();
}

bool Matching::isExposed(const DiagramPoint& p) const 
{
    return ( AToB.find(p) == AToB.end() ) && ( BToA.find(p) == BToA.end() );
}


BoundMatchOracle::BoundMatchOracle(DiagramPointSet psA, DiagramPointSet psB,
        double dEps, bool useRS) :
    A(psA), B(psB), M(A, B), distEpsilon(dEps), useRangeSearch(useRS), prevQueryValue(0.0)
{
    neighbOracle = new NeighbOracle(psB, 0, distEpsilon);
}

bool BoundMatchOracle::isMatchLess(double r)
{
    return buildMatchingForThreshold(r);
}


void BoundMatchOracle::removeFromLayer(const DiagramPoint& p, const int layerIdx) {
    //bool isDebug {false};
    //printDebug(isDebug, "entered removeFromLayer, layerIdx == " + std::to_string(layerIdx) + ", p = ", p);
    layerGraph[layerIdx].erase(p);
    if (layerOracles[layerIdx]) {
        layerOracles[layerIdx]->deletePoint(p);
    }
}

// return true, if there exists an augmenting path from startVertex
// in this case the path is returned in result.
// startVertex must be an exposed vertex from L_1 (layer[0])
bool BoundMatchOracle::buildAugmentingPath(const DiagramPoint startVertex, Path& result)
{
    //bool isDebug {false};
    //printDebug(isDebug, "Entered buildAugmentingPath, startVertex: ", startVertex);
    DiagramPoint prevVertexA = startVertex;
    result.clear();
    result.push_back(startVertex);
    size_t evenLayerIdx {1};
    while ( evenLayerIdx < layerGraph.size() ) {
    //for(size_t evenLayerIdx = 1; evenLayerIdx < layerGraph.size(); evenLayerIdx += 2) {
        DiagramPoint nextVertexB{0.0, 0.0, DiagramPoint::DIAG, 1}; // next vertex from even layer
        bool neighbFound = layerOracles[evenLayerIdx]->getNeighbour(prevVertexA, nextVertexB);
        //printDebug(isDebug, "Searched neighbours for ", prevVertexA);
        //printDebug(isDebug, "; the result is ", nextVertexB);
        if (neighbFound) {
           result.push_back(nextVertexB);
           if ( layerGraph.size() == evenLayerIdx + 1) {
                //printDebug(isDebug, "Last layer reached, stopping; the path: ", result);
                break;
            } else {
                 // nextVertexB must be matched with some vertex from the next odd
                 // layer
                DiagramPoint nextVertexA {0.0, 0.0, DiagramPoint::DIAG, 1};
                if (!M.getMatchedVertex(nextVertexB, nextVertexA)) {
                    std::cerr << "Vertices in even layers must be matched! Unmatched: ";
                    std::cerr << nextVertexB << std::endl;
                    std::cerr << evenLayerIdx << "; " << layerGraph.size() << std::endl;
                    throw "Unmatched vertex in even layer";
                } else {
                    assert( ! (nextVertexA.getRealX() == 0 and nextVertexA.getRealY() == 0) );
                    result.push_back(nextVertexA);
                    //printDebug(isDebug, "Matched vertex from the even layer added to the path, result: ", result);
                    prevVertexA = nextVertexA;
                    evenLayerIdx += 2;
                    continue;
                }
            }
        } else {
            // prevVertexA has no neighbours in the next layer,
            // backtrack
            if (evenLayerIdx == 1) {
                // startVertex is not connected to any vertices
                // in the next layer, augm. path doesn't exist
                //printDebug(isDebug, "startVertex is not connected to any vertices in the next layer, augm. path doesn't exist");
                removeFromLayer(startVertex, 0);
                return false;
            } else {
                assert(evenLayerIdx >= 3);
                assert(result.size() % 2 == 1);
                result.pop_back();
                DiagramPoint prevVertexB = result.back();
                result.pop_back();
                //printDebug(isDebug, "removing 2 previous vertices from layers, evenLayerIdx == ", evenLayerIdx);
                removeFromLayer(prevVertexA, evenLayerIdx-1);
                removeFromLayer(prevVertexB, evenLayerIdx-2);
                // we should proceed from the previous odd layer
                //printDebug(isDebug, "Here! res.size == ", result.size());
                assert(result.size() >= 1);
                prevVertexA = result.back();
                evenLayerIdx -= 2;
                continue;
            }
        }
    } // finished iterating over all layers
    // remove all vertices in the augmenting paths
    // the corresponding layers
    for(size_t layerIdx = 0; layerIdx < result.size(); ++layerIdx) {
        removeFromLayer(result[layerIdx], layerIdx);
    }
    return true;
}


// remove all edges whose length is > newThreshold
void Matching::trimMatching(const double newThreshold)
{
    //bool isDebug { false };
    sanityCheck();
    for(auto aToBIter = AToB.begin(); aToBIter != AToB.end(); ) {
        if ( distLInf(aToBIter->first, aToBIter->second) > newThreshold ) {
            // remove edge from AToB and BToA
            //printDebug(isDebug, "removing edge ", aToBIter->first);
            //printDebug(isDebug, " <-> ", aToBIter->second);
            BToA.erase(aToBIter->second);
            aToBIter = AToB.erase(aToBIter);
        } else {
            aToBIter++;
        }
    }
    sanityCheck();
}

bool BoundMatchOracle::buildMatchingForThreshold(const double r) 
{
    //bool isDebug {false};
    //printDebug(isDebug,"Entered buildMatchingForThreshold, r = " + std::to_string(r));
    if (prevQueryValue > r) {
        M.trimMatching(r);
    }
    prevQueryValue = r;
    while(true) {
        buildLayerGraph(r);
        //printDebug(isDebug,"Layer graph built");
        if (augPathExist) {
            std::vector<Path> augmentingPaths;
            DiagramPointSet copyLG0;
            for(DiagramPoint p : layerGraph[0]) {
                copyLG0.insert(p);
            }
            for(DiagramPoint exposedVertex : copyLG0) {
                Path augPath;
                if (buildAugmentingPath(exposedVertex, augPath)) {
                    //printDebug(isDebug, "Augmenting path found", augPath);
                    augmentingPaths.push_back(augPath);
                } 
                /*
                else {
                    printDebug(isDebug,"augmenting paths must exist, but were not found!", M);
                    std::cerr << "augmenting paths must exist, but were not found!" << std::endl;
                    std::cout.flush();
                    std::cerr.flush();
                    printLayerGraph();
                    //throw "Something went wrong-1";
                    //return M.isPerfect();
                    // analyze: finished or no paths exist
                    // can this actually happen?
                }
                */
                
            } 
            if (augmentingPaths.empty()) {
                //printDebug(isDebug,"augmenting paths must exist, but were not found!", M);
                std::cerr << "augmenting paths must exist, but were not found!" << std::endl;
                throw "bad epsilon?";
            }
            // swap all augmenting paths with matching to increase it
            //printDebug(isDebug,"before increase with augmenting paths:", M);
            for(auto& augPath : augmentingPaths ) {
                //printDebug(isDebug, "Increasing with augm. path ", augPath);
                M.increase(augPath);
            }
            //printDebug(isDebug,"after increase with augmenting paths:", M);
        } else {
            //printDebug(isDebug,"no augmenting paths exist, matching returned is:", M);
            return M.isPerfect();
        }
    } 
}

void BoundMatchOracle::printLayerGraph(void)
{
#ifdef DEBUG_BOUND_MATCH
    for(auto& layer : layerGraph) {
        std::cout << "{ ";
        for(auto& p : layer) {
            std::cout << p << "; ";
        }
        std::cout << "\b\b }" << std::endl;
    }
#endif
}

void BoundMatchOracle::buildLayerGraph(double r)
{
    //bool isDebug {false};
    //printDebug(isDebug,"Entered buildLayerGraph");
    layerGraph.clear();
    DiagramPointSet L1 = M.getExposedVertices();
    //printDebug(isDebug,"Got exposed vertices");
    layerGraph.push_back(L1);
    neighbOracle->rebuild(B, r);
    //printDebug(isDebug,"Oracle rebuilt");
    size_t k = 0;
    DiagramPointSet layerNextEven;
    DiagramPointSet layerNextOdd;
    bool exposedVerticesFound {false};
    while(true) {
        //printDebug(isDebug, "k = ", k);
        layerNextEven.clear();
        for( auto p : layerGraph[k]) {
            //printDebug(isDebug,"looking for neighbours for ", p);
            bool neighbFound;
            DiagramPoint neighbour {0.0, 0.0, DiagramPoint::DIAG, 1};
            if (useRangeSearch) {
                std::vector<DiagramPoint> neighbVec;
                neighbOracle->getAllNeighbours(p, neighbVec);
                neighbFound = !neighbVec.empty();
                for(auto& neighbPt : neighbVec) {
                    layerNextEven.insert(neighbPt);
                    if (!exposedVerticesFound and M.isExposed(neighbPt))
                        exposedVerticesFound = true;
                }
            } else {
                while(true) {
                    neighbFound = neighbOracle->getNeighbour(p, neighbour);
                    if (neighbFound) {
                        //printDebug(isDebug,"neighbour found, ", neighbour);
                        layerNextEven.insert(neighbour);
                        neighbOracle->deletePoint(neighbour);
                        //printDebug(isDebug,"is exposed: "  + std::to_string(M.isExposed(neighbour)));
                        if ((!exposedVerticesFound) && M.isExposed(neighbour)) {
                            exposedVerticesFound = true;
                        }
                    } else {
                        //printDebug(isDebug,"no neighbours found for r = ", r);
                        break;
                    }
                }
            } // without range search
        } // all vertices from previous odd layer processed
        //printDebug(isDebug,"Next even layer finished");
        if (layerNextEven.empty()) {
            //printDebug(isDebug,"Next even layer is empty, augPathExist = false");
            augPathExist = false;
            break;  
        }
        if (exposedVerticesFound) {
            //printDebug(isDebug,"Exposed vertices found in the even layer, aug. paths exist");
            //printDebug(isDebug,"Deleting all non-exposed from the last layer (we do not need them).");
            for(auto it = layerNextEven.cbegin(); it != layerNextEven.cend(); ) {
                if ( ! M.isExposed(*it) ) {
                    layerNextEven.erase(it++);
                } else {
                    ++it;
                }

            }
            layerGraph.push_back(layerNextEven);
            augPathExist = true;
            break;
        }
        layerGraph.push_back(layerNextEven);
        M.getAllAdjacentVertices(layerNextEven, layerNextOdd);
        //printDebug(isDebug,"Next odd layer finished");
        layerGraph.push_back(layerNextOdd);
        k += 2;
    }
    buildLayerOracles(r);
    //printDebug(isDebug,"layer oracles built, layer graph:");
    printLayerGraph();
}



BoundMatchOracle::~BoundMatchOracle()
{
    for(auto& oracle : layerOracles) {
        delete oracle;
    }
    delete neighbOracle;
}

// create geometric oracles for each even layer
// odd layers have NULL in layerOracles
void BoundMatchOracle::buildLayerOracles(double r)
{
    //bool isDebug {false};
    //printDebug(isDebug,"entered buildLayerOracles");
    // free previously constructed oracles
    for(auto& oracle : layerOracles) {
        delete oracle;
    }
    layerOracles.clear();
    //printDebug(isDebug,"previous oracles deleted");
    for(size_t layerIdx = 0; layerIdx < layerGraph.size(); ++layerIdx) {
        if (layerIdx % 2 == 1) {
            // even layer, build actual oracle
            layerOracles.push_back(new NeighbOracle(layerGraph[layerIdx], r, distEpsilon));
        } else {
            // odd layer
            layerOracles.push_back(nullptr);
        }
    }
    //printDebug(isDebug,"exiting buildLayerOracles");
}
}
