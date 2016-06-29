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


#ifndef BASIC_DEFS_BT_H
#define BASIC_DEFS_BT_H

#ifdef _WIN32
#include <ciso646>
#endif

#include <vector>
#include <math.h>
#include <cstddef>
#include <unordered_map>
#include <unordered_set>
#include <iostream>
#include <string>
#include <assert.h>

#include "def_debug.h"


namespace geom_bt {

typedef double CoordinateType;
typedef int IdType;
constexpr IdType MinValidId  = 10;

struct Point {
    CoordinateType x, y;
    bool operator==(const Point& other) const;
    bool operator!=(const Point& other) const;
    Point(CoordinateType ax, CoordinateType ay) : x(ax), y(ay) {}
    Point() : x(0.0), y(0.0) {}
    friend std::ostream& operator<<(std::ostream& output, const Point p);
};

struct DiagramPoint 
{
    // Points above the diagonal have type NORMAL
    // Projections onto the diagonal have type DIAG
    // for DIAG points only x-coordinate is relevant
    // to-do: add getters/setters, checks in constructors, etc
    enum Type { NORMAL, DIAG};
    // data members
private:
    CoordinateType x, y;
public:
    Type type;
    IdType id;
    // operators, constructors
    bool operator==(const DiagramPoint& other) const;
    bool operator!=(const DiagramPoint& other) const;
    DiagramPoint(CoordinateType xx, CoordinateType yy, Type ttype, IdType uid);
    bool isDiagonal(void) const { return type == DIAG; }
    bool isNormal(void) const { return type == NORMAL; }
    CoordinateType inline getRealX() const // return the x-coord
    {
        return x;
        //if (DiagramPoint::NORMAL == type)
            //return x;
        //else 
            //return 0.5 * ( x + y);
    }    

    CoordinateType inline getRealY() const // return the y-coord
    {
        return y;
        //if (DiagramPoint::NORMAL == type)
            //return y;
        //else 
            //return 0.5 * ( x + y);
    }

    friend std::ostream& operator<<(std::ostream& output, const DiagramPoint p);
};

struct PointHash {
    size_t operator()(const Point& p) const{
        return std::hash<CoordinateType>()(p.x)^std::hash<CoordinateType>()(p.y);
    }
};

struct DiagramPointHash {
    size_t operator()(const DiagramPoint& p) const{
        //return std::hash<CoordinateType>()(p.x)^std::hash<CoordinateType>()(p.y)^std::hash<bool>()(p.type == DiagramPoint::NORMAL);
        assert(p.id >= MinValidId);
        return std::hash<int>()(p.id);
    }
};

CoordinateType sqrDist(const Point& a, const Point& b);
CoordinateType dist(const Point& a, const Point& b);
CoordinateType distLInf(const DiagramPoint& a, const DiagramPoint& b);

typedef std::unordered_set<Point, PointHash> PointSet;

class DiagramPointSet {
public:
    void insert(const DiagramPoint p);
    void erase(const DiagramPoint& p, bool doCheck = true); // if doCheck, erasing non-existing elements causes assert
    void erase(const std::unordered_set<DiagramPoint, DiagramPointHash>::const_iterator it);
    void removeDiagonalPoints();
    size_t size() const;
    void reserve(const size_t newSize);
    void clear();
    bool empty() const;
    bool hasElement(const DiagramPoint& p) const;
    std::unordered_set<DiagramPoint, DiagramPointHash>::iterator find(const DiagramPoint& p) { return points.find(p); };
    std::unordered_set<DiagramPoint, DiagramPointHash>::const_iterator find(const DiagramPoint& p) const { return points.find(p); };
    std::unordered_set<DiagramPoint, DiagramPointHash>::iterator begin() { return points.begin(); };
    std::unordered_set<DiagramPoint, DiagramPointHash>::iterator end() { return points.end(); }
    std::unordered_set<DiagramPoint, DiagramPointHash>::const_iterator cbegin() const { return points.cbegin(); }
    std::unordered_set<DiagramPoint, DiagramPointHash>::const_iterator cend() const { return points.cend(); }
    friend std::ostream& operator<<(std::ostream& output, const DiagramPointSet& ps);
    friend void addProjections(DiagramPointSet& A, DiagramPointSet& B);
    template<class PairIterator> DiagramPointSet(PairIterator first, PairIterator last);
    template<class PairIterator> void fillIn(PairIterator first, PairIterator last);
    // default ctor, empty diagram
    DiagramPointSet(IdType minId = MinValidId + 1) : maxId(minId + 1) {};
    IdType nextId() { return maxId + 1; }
private:
    bool isLinked { false };
    IdType maxId {MinValidId + 1};
    std::unordered_set<DiagramPoint, DiagramPointHash> points;
};

template<typename DiagPointContainer>
CoordinateType getFurthestDistance3Approx(DiagPointContainer& A, DiagPointContainer& B)
{
    CoordinateType result { 0.0 };
    DiagramPoint begA = *(A.begin());
    DiagramPoint optB = *(B.begin());
    for(const auto& pointB : B) {
        if (distLInf(begA, pointB) > result) {
            result = distLInf(begA, pointB);
            optB = pointB;
        }
    }
    for(const auto& pointA : A) {
        if (distLInf(pointA, optB) > result) {
            result = distLInf(pointA, optB);
        }
    }
    return result;
}

template<class PairIterator>
void DiagramPointSet::fillIn(PairIterator start, PairIterator end)
{
    isLinked = false;
    clear();
    IdType uniqueId = MinValidId + 1;
    for(auto iter = start; iter != end; ++iter) {
        insert(DiagramPoint(iter->first, iter->second, DiagramPoint::NORMAL, uniqueId++));
    }
}

template<class PairIterator>
DiagramPointSet::DiagramPointSet(PairIterator start, PairIterator end) 
{
    fillIn(start, end);
}

// preprocess diagrams A and B by adding projections onto diagonal of points of
// A to B and vice versa. NB: ids of points will be changed!
void addProjections(DiagramPointSet& A, DiagramPointSet& B);

}
#endif
