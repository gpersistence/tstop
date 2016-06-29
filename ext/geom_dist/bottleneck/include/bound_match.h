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

#ifndef BOUND_MATCH_H
#define BOUND_MATCH_H

#include <unordered_map>

#include "basic_defs_bt.h"
#include "neighb_oracle.h"


namespace geom_bt {
typedef std::vector<DiagramPoint> Path;

class Matching {
public:
    Matching(const DiagramPointSet& AA, const DiagramPointSet& BB) : A(AA), B(BB) {};
    DiagramPointSet getExposedVertices(bool forA = true) const ;
    bool isExposed(const DiagramPoint& p) const;
    void getAllAdjacentVertices(const DiagramPointSet& setIn, DiagramPointSet& setOut, bool forA = true) const;
    void increase(const Path& augmentingPath);
    void checkAugPath(const Path& augPath) const;
    bool getMatchedVertex(const DiagramPoint& p, DiagramPoint& result) const;
    bool isPerfect() const;
    void trimMatching(const double newThreshold);
    friend std::ostream& operator<<(std::ostream& output, const Matching& m);
private:
    DiagramPointSet A;
    DiagramPointSet B;
    std::unordered_map<DiagramPoint, DiagramPoint, DiagramPointHash> AToB, BToA;
    void matchVertices(const DiagramPoint& pA, const DiagramPoint& pB);
    void sanityCheck() const;
};



class BoundMatchOracle {
public:
    BoundMatchOracle(DiagramPointSet psA, DiagramPointSet psB, double dEps, bool useRS = true);
    bool isMatchLess(double r);
    void setInnerOracle(NeighbOracleAbstract* innerOracle) { neighbOracle = innerOracle; }
    bool buildMatchingForThreshold(const double r);
    ~BoundMatchOracle();
private:
    DiagramPointSet A, B;
    Matching M;
    void printLayerGraph(void);
    void buildLayerGraph(double r);
    void buildLayerOracles(double r);
    bool buildAugmentingPath(const DiagramPoint startVertex, Path& result);
    void removeFromLayer(const DiagramPoint& p, const int layerIdx);
    NeighbOracleAbstract* neighbOracle;
    bool augPathExist;
    std::vector<DiagramPointSet> layerGraph;
    std::vector<NeighbOracle*> layerOracles;
    double distEpsilon;
    bool useRangeSearch;
    double prevQueryValue;
};

}
#endif
