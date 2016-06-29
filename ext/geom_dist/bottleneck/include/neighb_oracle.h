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

#ifndef NEIGHB_ORACLE_H
#define NEIGHB_ORACLE_H

#include <unordered_map>
#include "basic_defs_bt.h"
#include <ANN/ANN.h>

namespace geom_bt {
class NeighbOracleAbstract{
public:
    virtual void deletePoint(const DiagramPoint& p) = 0;
    virtual void rebuild(const DiagramPointSet& S, double rr) = 0;
    // return true, if r-neighbour of q exists in pointSet,
    // false otherwise.
    // the neighbour is returned in result
    virtual bool getNeighbour(const DiagramPoint& q, DiagramPoint& result) const = 0;
    virtual void getAllNeighbours(const DiagramPoint& q, std::vector<DiagramPoint>& result) = 0;
    virtual ~NeighbOracleAbstract() {};
protected:
    double r;
    double distEpsilon;
};

class NeighbOracleSimple : public NeighbOracleAbstract
{
public:
    NeighbOracleSimple();
    NeighbOracleSimple(const DiagramPointSet& S, const double rr, const double dEps);
    void deletePoint(const DiagramPoint& p);
    void rebuild(const DiagramPointSet& S, const double rr);
    bool getNeighbour(const DiagramPoint& q, DiagramPoint& result) const;
    void getAllNeighbours(const DiagramPoint& q, std::vector<DiagramPoint>& result);
    ~NeighbOracleSimple() {};
private:
    DiagramPointSet pointSet;
};

class NeighbOracleAnn : public NeighbOracleAbstract
{
public:
    NeighbOracleAnn(const DiagramPointSet& S, const double rr, const double dEps);
    void deletePoint(const DiagramPoint& p);
    void rebuild(const DiagramPointSet& S, const double rr);
    bool getNeighbour(const DiagramPoint& q, DiagramPoint& result) const;
    void getAllNeighbours(const DiagramPoint& q, std::vector<DiagramPoint>& result);
    ~NeighbOracleAnn();
//private:
    //DiagramPointSet originalPointSet;
    std::vector<DiagramPoint> allPoints;
    DiagramPointSet diagonalPoints;
    std::unordered_map<DiagramPoint, size_t, DiagramPointHash> pointIdxLookup;
    // ann-stuff
    static constexpr double annEpsilon {0};
    static const int annK {1};
    static const int annDim{2};
    ANNpointArray annPoints;
    ANNkd_tree* kdTree;
    ANNidxArray annNeigbIndices;
    ANNpoint annQueryPoint;
    // to use in getAllNeighbours
    ANNpoint lo;
    ANNpoint hi;
    ANNidxArray annIndices;
    ANNdistArray annDistances;
};

//typedef NeighbOracleSimple NeighbOracle;
typedef NeighbOracleAnn NeighbOracle;

}
#endif
