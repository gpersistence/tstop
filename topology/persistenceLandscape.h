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



//    Copyright 2013-2014 University of Pennsylvania
//    Created by Pawel Dlotko
//
//    This file is part of Persistence Landscape Toolbox (PLT).
//
//    PLT is free software: you can redistribute it and/or modify
//    it under the terms of the GNU Lesser General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    PLT is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU Lesser General Public License for more details.
//
//    You should have received a copy of the GNU Lesser General Public License
//    along with PLT.  If not, see <http://www.gnu.org/licenses/>.




#pragma once

#ifndef PERISTENCELANDSCAPE_H
#define PERISTENCELANDSCAPE_H


#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include <algorithm>
#include <cmath>
#include <list>
#include <climits>
#include <limits>
#include <cstdarg>
#include <iomanip>
//#include "configure.h"
#include "persistenceBarcode.h"


extern double epsi;

inline bool almostEqual( double a , double b )
{
    if ( fabs(a-b) < epsi )
        return true;
    return false;
}


double birth ( std::pair<double,double> a )
{
    return a.first-a.second;
}

double death( std::pair<double,double> a )
{
    return a.first+a.second;
}


//functions used in PersistenceLandscape( const PersistenceBarcodes& p ) constructor:
bool comparePointsDBG = false;
bool comparePoints( std::pair<double,double> f, std::pair<double,double> s )
{
    double differenceBirth = birth(f)-birth(s);
    if ( differenceBirth < 0 )differenceBirth *= -1;
    double differenceDeath = death(f)-death(s);
    if ( differenceDeath < 0 )differenceDeath *= -1;

    if ( (differenceBirth < epsi) && (differenceDeath < epsi)  )
    {
        if(comparePointsDBG){std::cerr << "CP1 \n";}
        return false;
    }
    if ( (differenceBirth < epsi) )
    {
        //consider birth points the same. If we are here, we know that death points are NOT the same
        if ( death(f) < death(s) )
        {
            if(comparePointsDBG){std::cerr << "CP2 \n";}
            return true;
        }
        if(comparePointsDBG){std::cerr << "CP3 \n";}
        return false;
    }
    if ( differenceDeath < epsi )
    {
        //we consider death points the same and since we are here, the birth points are not the same!
        if ( birth(f) < birth(s) )
        {
            if(comparePointsDBG){std::cerr << "CP4 \n";}
            return false;
        }
        if(comparePointsDBG){std::cerr << "CP5 \n";}
        return true;
    }

    if ( birth(f) > birth(s) )
    {
        if(comparePointsDBG){std::cerr << "CP6 \n";}
        return false;
    }
    if ( birth(f) < birth(s) )
    {
        if(comparePointsDBG){std::cerr << "CP7 \n";}
        return true;
    }
    //if this is true, we assume that death(f)<=death(s) -- othervise I have had a lot of roundoff problems here!
    if ( (death(f)<=death(s)) )
    {
        if(comparePointsDBG){std::cerr << "CP8 \n";}
        return false;
    }
    if(comparePointsDBG){std::cerr << "CP9 \n";}
    return true;
}



//this function assumes birth-death coords
bool comparePoints2( std::pair<double,double> f, std::pair<double,double> s )
{
    if ( f.first < s.first )
    {
        return true;
    }
    else
    {//f.first >= s.first
        if ( f.first > s.first )
        {
            return false;
        }
        else
        {//f.first == s.first
            if ( f.second > s.second )
            {
                return true;
            }
            else
            {
                return false;
            }
        }
    }
}




class vectorSpaceOfPersistenceLandscapes;

//functions used to add and subtract landscapes
inline double add(double x, double y){return x+y;}
inline double sub(double x, double y){return x-y;}

//function used in computeValueAtAGivenPoint
double functionValue ( std::pair<double,double> p1, std::pair<double,double> p2 , double x )
{
    //we assume here, that x \in [ p1.first, p2.first ] and p1 and p2 are points between which we will put the line segment
    double a = (p2.second - p1.second)/(p2.first - p1.first);
    double b = p1.second - a*p1.first;
    //cerr << "Line crossing points : (" << p1.first << "," << p1.second << ") oraz (" << p2.first << "," << p2.second << ") : \n";
    //cerr << "a : " << a << " , b : " << b << " , x : " << x << endl;
    return (a*x+b);
}

class PersistenceLandscape
{
public:
    bool testLandscape( const PersistenceBarcodes& b );//for tests only!

    PersistenceLandscape(){this->dimension = 0;}
    PersistenceLandscape( const PersistenceBarcodes& p );
    PersistenceLandscape operator=( const PersistenceLandscape& org );
    PersistenceLandscape(const PersistenceLandscape&);
    PersistenceLandscape(char* filename);

    PersistenceLandscape(std::vector< std::vector<std::pair<double,double> > > landscapePointsWithoutInfinities);
    std::vector< std::vector<std::pair<double,double> > > gimmeProperLandscapePoints();


    double computeIntegralOfLandscape()const;
    double computeIntegralOfLandscape( double p )const;//this function compute integral of p-th power of landscape.
    double computeIntegralOfLandscapeMultipliedByIndicatorFunction( std::vector<std::pair<double,double> > indicator )const;
    double computeIntegralOfLandscapeMultipliedByIndicatorFunction( std::vector<std::pair<double,double> > indicator,double p )const;//this function compute integral of p-th power of landscape multiplied by the indicator function.
    PersistenceLandscape multiplyByIndicatorFunction( std::vector<std::pair<double,double> > indicator )const;

    unsigned removePairsOfLocalMaximumMinimumOfEpsPersistence(double errorTolerance);
    void reduceAllPairsOfLowPersistenceMaximaMinima( double epsilon );
    void reduceAlignedPoints(double tollerance = 0.000001);
    unsigned reducePoints( double tollerance , double (*penalty)(std::pair<double,double> ,std::pair<double,double>,std::pair<double,double>) );
    double computeValueAtAGivenPoint( unsigned level , double x )const;
    friend std::ostream& operator<<(std::ostream& out, PersistenceLandscape& land );

    void computeLandscapeOnDiscreteSetOfPoints( PersistenceBarcodes& b , double dx );

    typedef std::vector< std::pair<double,double> >::iterator lDimIterator;
    lDimIterator lDimBegin(unsigned dim)
    {
        if ( dim > this->land.size() )throw("Calling lDimIterator in a dimension higher that dimension of landscape");
        return this->land[dim].begin();
    }
    lDimIterator lDimEnd(unsigned dim)
    {
        if ( dim > this->land.size() )throw("Calling lDimIterator in a dimension higher that dimension of landscape");
        return this->land[dim].end();
    }

    PersistenceLandscape multiplyLanscapeByRealNumberNotOverwrite( double x )const;
    void multiplyLanscapeByRealNumberOverwrite( double x );

    void plot( char* filename ,size_t from=-1, size_t to=-1 ,  double xRangeBegin = -1 , double xRangeEnd = -1 , double yRangeBegin = -1 , double yRangeEnd = -1 );


    PersistenceBarcodes convertToBarcode();
//Friendzone:

    //this is a general algorithm to perform linear operations on persisntece lapscapes. It perform it by doing operations on landscape points.
    friend PersistenceLandscape operationOnPairOfLandscapes ( const PersistenceLandscape& land1 ,  const PersistenceLandscape& land2 , double (*oper)(double,double) );

    friend PersistenceLandscape addTwoLandscapes ( const PersistenceLandscape& land1 ,  const PersistenceLandscape& land2 )
    {
        return operationOnPairOfLandscapes(land1,land2,add);
    }
    friend PersistenceLandscape subtractTwoLandscapes ( const PersistenceLandscape& land1 ,  const PersistenceLandscape& land2 )
    {
        return operationOnPairOfLandscapes(land1,land2,sub);
    }

    friend PersistenceLandscape operator+( const PersistenceLandscape& first , const PersistenceLandscape& second )
    {
        return addTwoLandscapes( first,second );
    }

    friend PersistenceLandscape operator-( const PersistenceLandscape& first , const PersistenceLandscape& second )
    {
        return subtractTwoLandscapes( first,second );
    }

    friend PersistenceLandscape operator*( const PersistenceLandscape& first , double con )
    {
        return first.multiplyLanscapeByRealNumberNotOverwrite(con);
    }

    friend PersistenceLandscape operator*( double con , const PersistenceLandscape& first  )
    {
        return first.multiplyLanscapeByRealNumberNotOverwrite(con);
    }

    PersistenceLandscape operator += ( const PersistenceLandscape& rhs )
    {
        *this = *this + rhs;
        return *this;
    }

    PersistenceLandscape operator -= ( const PersistenceLandscape& rhs )
    {
        *this = *this - rhs;
        return *this;
    }


    PersistenceLandscape operator *= ( double x )
    {
        *this = *this*x;
        return *this;
    }

    PersistenceLandscape operator /= ( double x )
    {
        if ( x == 0 )throw( "In operator /=, division by 0. Program terminated." );
        *this = *this * (1/x);
        return *this;
    }

    bool operator == ( const PersistenceLandscape& rhs  )const;

    double computeMaximum()const
    {
        double maxValue = 0;
        if ( this->land.size() )
        {
            maxValue = -INT_MAX;
            for ( size_t i = 0 ; i != this->land[0].size() ; ++i )
            {
                if ( this->land[0][i].second > maxValue )maxValue = this->land[0][i].second;
            }
        }
        return maxValue;
    }

    double computeNormOfLandscape( int i )
    {
        PersistenceLandscape l;
        if ( i != -1 )
        {
            return computeDiscanceOfLandscapes(*this,l,i);
        }
        else
        {
            return computeMaxNormDiscanceOfLandscapes(*this,l);
        }
    }

    double operator()(unsigned level,double x)const{return this->computeValueAtAGivenPoint(level,x);}

    friend double computeMaxNormDiscanceOfLandscapes( const PersistenceLandscape& first, const PersistenceLandscape& second );
    friend double computeMaxNormDiscanceOfLandscapes( const PersistenceLandscape& first, const PersistenceLandscape& second , unsigned& nrOfLand , double&x , double& y1, double& y2 );

    friend double computeDiscanceOfLandscapes( const PersistenceLandscape& first, const PersistenceLandscape& second , unsigned p );

    friend double computeMaximalDistanceNonSymmetric( const PersistenceLandscape& pl1, const PersistenceLandscape& pl2 );

    friend double computeMaximalDistanceNonSymmetric( const PersistenceLandscape& pl1, const PersistenceLandscape& pl2 , unsigned& nrOfLand , double&x , double& y1, double& y2 );
    //this function additionally returns integer n and double x, y1, y2 such that the maximal distance is obtained betwenn lambda_n's on a coordinate x
    //such that the value of the first landscape is y1, and the vale of the second landscape is y2.


    friend class vectorSpaceOfPersistenceLandscapes;

    unsigned dim()const{return this->dimension;}

    double minimalNonzeroPoint( unsigned l )const
    {
        if ( this->land.size() < l )return INT_MAX;
        return this->land[l][1].first;
    }

    double maximalNonzeroPoint( unsigned l )const
    {
        if ( this->land.size() < l )return INT_MIN;
        return this->land[l][ this->land[l].size()-2 ].first;
    }

    PersistenceLandscape abs();

    size_t size()const{return this->land.size(); }

    double findMax( unsigned lambda )const;


    //visualization part...
    void printToFiles( const char* filename , unsigned from , unsigned to )const;
    void printToFiles( const char* filename )const;
    void printToFiles( const char* filename, int numberOfElementsLater,  ... )const;
    void printToFile( const char* filename , unsigned from , unsigned to )const;
    void printToFile( const char* filename )const;
    void generateGnuplotCommandToPlot( const char* filename , unsigned from , unsigned to )const;
    void generateGnuplotCommandToPlot(const char* filename)const;
    void generateGnuplotCommandToPlot(const char* filename,int numberOfElementsLater,  ... )const;

    //this function compute n-th moment of lambda_level
    double computeNthMoment( unsigned n , double center , unsigned level )const;

   //those are two new functions to generate histograms of Betti numbers across the filtration values.
    std::vector< std::pair< double , unsigned > > generateBettiNumbersHistogram()const;
    void printBettiNumbersHistoramIntoFileAndGenerateGnuplotCommand( char* filename )const;
private:
    std::vector< std::vector< std::pair<double,double> > > land;
    unsigned dimension;
};


void PersistenceLandscape::plot( char* filename , size_t from, size_t to , double xRangeBegin , double xRangeEnd , double yRangeBegin , double yRangeEnd )
{
    //this program create a gnuplot script file that allows to plot persistence diagram.
    std::ofstream out;

    std::ostringstream nameSS;
    nameSS << filename << "_GnuplotScript";
    std::string nameStr = nameSS.str();
    out.open( (char*)nameStr.c_str() );

    if ( (xRangeBegin != -1) || (xRangeEnd != -1) || (yRangeBegin != -1) || (yRangeEnd != -1)  )
    {
      out << "set xrange [" << xRangeBegin << " : " << xRangeEnd << "]" << std::endl;
      out << "set yrange [" << yRangeBegin << " : " << yRangeEnd << "]" << std::endl;
    }

    if ( from == -1 ){from = 0;}
    if ( to == -1 ){to = this->land.size();}

    out << "plot ";
    for ( size_t lambda= std::min(from,this->land.size()) ; lambda != std::min(to,this->land.size()) ; ++lambda )
    {
        out << "     '-' using 1:2 title 'l" << lambda << "' with lp";
        if ( lambda+1 != std::min(to,this->land.size()) )
        {
            out << ", \\";
        }
        out << std::endl;
    }

    for ( size_t lambda= std::min(from,this->land.size()) ; lambda != std::min(to,this->land.size()) ; ++lambda )
    {
        for ( size_t i = 1 ; i != this->land[lambda].size()-1 ; ++i )
        {
            out << this->land[lambda][i].first << " " << this->land[lambda][i].second << std::endl;
        }
        out << "EOF" << std::endl;
    }
    std::cout << "Gnuplot script to visualize persistence diagram written to the file: " << nameStr << ". Type load '" << nameStr << "' in gnuplot to visualize." << std::endl;
}


PersistenceLandscape::PersistenceLandscape(std::vector< std::vector<std::pair<double,double> > > landscapePointsWithoutInfinities)
{
    for ( size_t level = 0 ; level != landscapePointsWithoutInfinities.size() ; ++level )
    {
        std::vector< std::pair<double,double> > v;
        v.push_back(std::make_pair(INT_MIN,0));
        v.insert( v.end(), landscapePointsWithoutInfinities[level].begin(), landscapePointsWithoutInfinities[level].end() );
        v.push_back(std::make_pair(INT_MAX,0));
        this->land.push_back( v );
    }
    this->dimension = 0;
}

std::vector< std::vector<std::pair<double,double> > > PersistenceLandscape::gimmeProperLandscapePoints()
{
    std::vector< std::vector<std::pair<double,double> > > result;
    for ( size_t level = 0  ; level != this->land.size() ; ++level )
    {
        std::vector< std::pair<double,double> > v( this->land[level].begin()+1 , this->land[level].end()-1 );
        result.push_back(v);
    }
    return result;
}


//CAUTION, this procedure do not work yet. Please do not use it until this warning is removed.
PersistenceBarcodes PersistenceLandscape::convertToBarcode()
{
    bool dbg = false;
    //for the first level, find local maxima. They are points of the diagram. Find local minima and put them to the vector v
    //for every next level, find local maxima and put them to the list L. Find local minima and put them to the list v2
    //Point belong to the persistence barcode if it belong to the list L, but do not belong to the list v. When you pick the peristence diagram points at this level,
    //set v = v2.
    //QUESTION -- is there any significnce of the points in those layers? They may give some layer-characteristic of a diagram and give a marriage between landscapes and diagrams.

    std::vector< std::pair< double,double > > persistencePoints;
    if ( this->land[0].size() )
    {
        std::vector< std::pair<double,double> > localMinimas;



        for ( size_t level = 0 ; level != this->land.size() ; ++level )
        {
            if ( dbg )
            {
                std::cerr << "\n\n\n Level : " << level << std::endl;
                std::cerr << "Here is the list of local minima : \n";
                for ( size_t i = 0 ; i != localMinimas.size() ; ++i )
                {
                    std::cerr << localMinimas[i] << " ";
                }
                std::cerr << "\n";
                getchar();
            }

            size_t localMinimaCounter = 0;
            std::vector< std::pair<double,double> > newLocalMinimas;
            for ( size_t i = 1 ; i != this->land[level].size()-1 ; ++i )
            {
                if ( dbg )
                {
                    std::cerr << "Considering a pair : " << this->land[level][i] << std::endl;
                }
                if ( this->land[level][i].second == 0 )continue;

                if ( (this->land[level][i].second > this->land[level][i-1].second) && (this->land[level][i].second > this->land[level][i+1].second) )
                {
                    //if this is a local maximum. The question is -- is it also a local minimum of a previous function?
                    bool isThisALocalMinimumOfThePreviousLevel = false;

                    if ( dbg )
                    {
                        std::cerr << "It is a local maximum. Now we are checking if it is also a local minimum of the previous function." << std::endl;
                    }

                    while ( (localMinimaCounter < localMinimas.size()) && (localMinimas[localMinimaCounter].first < this->land[level][i].first ) )
                    {
                        if ( dbg )
                        {
                            std::cerr << "Adding : " << localMinimas[localMinimaCounter] << " to new local minima \n";
                        }
                        newLocalMinimas.push_back( localMinimas[localMinimaCounter] );
                        ++localMinimaCounter;
                    }

                    if ( localMinimaCounter != localMinimas.size() )
                    {
                        if ( localMinimas[localMinimaCounter] == this->land[level][i] )
                        {
                            isThisALocalMinimumOfThePreviousLevel = true;
                            ++localMinimaCounter;
                        }
                    }
                    if ( !isThisALocalMinimumOfThePreviousLevel )
                    {
                        if ( dbg )
                        {
                            std::cerr << "It is not a local minimum of the previous level, so it is a point : " << birth(this->land[level][i]) << " ,  " << death(this->land[level][i]) <<
                            " in a persistence diagram! \n";
                        }
                        persistencePoints.push_back( std::make_pair(birth(this->land[level][i]), death(this->land[level][i]) ) );
                    }
                    if ( (dbg) && (isThisALocalMinimumOfThePreviousLevel) )
                    {
                        std::cerr << "It is a local minimum of the previous, so we do nothing \n";
                    }

                }
                if ( this->land[level][i].second != 0 )
                {
                    if ( (this->land[level][i].second < this->land[level][i-1].second) && (this->land[level][i].second < this->land[level][i+1].second) )
                    {
                        if ( dbg )
                        {
                            std::cerr << "This point is a local minimum, so we add it to a list of local minima.\n";
                        }
                        //local minimum
                        if ( localMinimas.size() )
                        {
                            while ( (localMinimaCounter < localMinimas.size()) && (localMinimas[localMinimaCounter].first < this->land[level][i].first) )
                            {
                                newLocalMinimas.push_back(localMinimas[localMinimaCounter]);
                                ++localMinimaCounter;
                            }
                        }
                        newLocalMinimas.push_back( this->land[level][i] );
                    }
                }

                //if one is larger and the other is smaller, then such a point should be consider as both local minimum and maximum.
                if (
                       ( (this->land[level][i].second < this->land[level][i-1].second) && (this->land[level][i].second > this->land[level][i+1].second) )
                       ||
                       ( (this->land[level][i].second > this->land[level][i-1].second) && (this->land[level][i].second < this->land[level][i+1].second) )
                   )
                {
                    //minimum part:
                    newLocalMinimas.push_back( this->land[level][i] );
                    //maximum part:
                    bool isThisALocalMinimumOfThePreviousLevel = false;
                    if ( dbg )
                    {
                        std::cerr << "It is a local maximum and the local minimum." << std::endl;
                    }

                    while ( (localMinimaCounter < localMinimas.size()) && (localMinimas[localMinimaCounter].first < this->land[level][i].first ) )
                    {
                        newLocalMinimas.push_back( localMinimas[localMinimaCounter] );
                        ++localMinimaCounter;
                    }
                    if ( localMinimaCounter != localMinimas.size() )
                    {
                        if ( localMinimas[localMinimaCounter] == this->land[level][i] )
                        {
                            isThisALocalMinimumOfThePreviousLevel = true;
                            ++localMinimaCounter;
                        }
                    }
                    if ( !isThisALocalMinimumOfThePreviousLevel )
                    {
                        if ( dbg )
                        {
                            std::cerr << "It is not a local minimum of the previous level, so it is a point in a persistence diagram! \n";
                        }
                        persistencePoints.push_back( std::make_pair(birth(this->land[level][i]), death(this->land[level][i]) ) );
                    }
                    if ( (dbg) && (isThisALocalMinimumOfThePreviousLevel) )
                    {
                        std::cerr << "It is a local minimum of the previous, so we do nothing \n";
                    }
                }
            }

            if (dbg)
            {
                std::cerr << "Exit the loop for this level, exchanging local minimas lists \n";
                std::cerr << "localMinimas.size() : " << localMinimas.size() << std::endl;
                std::cerr << "localMinimaCounter : " << localMinimaCounter << std::endl;
            }
            if ( localMinimas.size() )
            {
                while ( localMinimaCounter < localMinimas.size() )
                {
                    newLocalMinimas.push_back( localMinimas[localMinimaCounter] );
                    ++localMinimaCounter;
                }
            }
            std::cerr << "here \n";
            localMinimas.swap( newLocalMinimas );
            std::cerr << "Done\n";



        }
    }

    return PersistenceBarcodes(persistencePoints);
}//convertToBarcode



PersistenceLandscape::PersistenceLandscape(char* filename)
{
    bool dbg = false;

    if ( dbg )
    {
        std::cerr << "Using constructor : PersistenceLandscape(char* filename)" << std::endl;
    }

    //this constructor reads persistence landscape form a file. This file have to be created by this software beforehead
    std::ifstream in;
    in.open( filename );
    unsigned dimension;
    in >> dimension;
    this->dimension = dimension;
    std::string line;
    getline(in,line);

    std::vector< std::pair<double,double> > landscapeAtThisLevel;

    bool isThisAFirsLine = true;
    while (!in.eof())
    {
        getline(in,line);
        if ( !(line.length() == 0 || line[0] == '#') )
        {
            std::stringstream lineSS;
            lineSS << line;
            double beginn, endd;
            lineSS >> beginn;
            lineSS >> endd;
            //if ( beginn > endd )
            //{
            //    double b = beginn;
            //    beginn = endd;
            //    endd = b;
            //}
            landscapeAtThisLevel.push_back( std::make_pair( beginn , endd ) );
            if (dbg){std::cerr << "Reading a pont : " << beginn << " , " << endd << std::endl;}
        }
        else
        {
            if (dbg)
            {
                std::cout << "IGNORE LINE\n";
                getchar();
            }
            if ( !isThisAFirsLine )
            {
                landscapeAtThisLevel.push_back( std::make_pair( INT_MAX , 0 ) );
                this->land.push_back(landscapeAtThisLevel);
                std::vector< std::pair<double,double> > newLevelOdLandscape;
                landscapeAtThisLevel.swap(newLevelOdLandscape);
            }
            landscapeAtThisLevel.push_back( std::make_pair( INT_MIN , 0 ) );
            isThisAFirsLine = false;
        }
	}
	if ( landscapeAtThisLevel.size() > 1 )
    {
        //seems that the last line of the file is not finished with the newline sign. We need to put what we have in landscapeAtThisLevel to the constructed landscape.
        landscapeAtThisLevel.push_back( std::make_pair( INT_MAX , 0 ) );
        this->land.push_back(landscapeAtThisLevel);
    }

    in.close();
}


bool operatorEqualDbg = false;
bool PersistenceLandscape::operator == ( const PersistenceLandscape& rhs  )const
{
    if ( this->land.size() != rhs.land.size() )
    {
        if (operatorEqualDbg)std::cerr << "1\n";
        return false;
    }
    for ( size_t level = 0 ; level != this->land.size() ; ++level )
    {
        if ( this->land[level].size() != rhs.land[level].size() )
        {
            if (operatorEqualDbg)std::cerr << "this->land[level].size() : " << this->land[level].size() <<  "\n";
            if (operatorEqualDbg)std::cerr << "rhs.land[level].size() : " << rhs.land[level].size() <<  "\n";
            if (operatorEqualDbg)std::cerr << "2\n";
            return false;
        }
        for ( size_t i = 0 ; i != this->land[level].size() ; ++i )
        {
            if ( this->land[level][i] != rhs.land[level][i] )
            {
                if (operatorEqualDbg)std::cerr << "this->land[level][i] : " << this->land[level][i] << "\n";
                if (operatorEqualDbg)std::cerr << "rhs.land[level][i] : " << rhs.land[level][i] << "\n";
                if (operatorEqualDbg)std::cerr << "3\n";
                return false;
            }
        }
    }
    return true;
}

//this function find maximum of lambda_n
double PersistenceLandscape::findMax( unsigned lambda )const
{
    if ( this->land.size() < lambda )return 0;
    double maximum = INT_MIN;
    for ( size_t i = 0 ; i != this->land[lambda].size() ; ++i )
    {
        if ( this->land[lambda][i].second > maximum )maximum = this->land[lambda][i].second;
    }
    return maximum;
}

//this function compute n-th moment of lambda_level
bool computeNthMomentDbg = true;
double PersistenceLandscape::computeNthMoment( unsigned n , double center , unsigned level )const
{
    if ( n < 1 )
    {
      std::cerr << "Cannot compute n-th moment for  n = " << n << ". The program will now terminate \n";
        throw("Cannot compute n-th moment. The program will now terminate \n");
    }
    double result = 0;
    if ( this->land.size() > level )
    {
        for ( size_t i = 2 ; i != this->land[level].size()-1 ; ++i )
        {
            if ( this->land[level][i].first - this->land[level][i-1].first == 0 )continue;
            //between this->land[level][i] and this->land[level][i-1] the lambda_level is of the form ax+b. First we need to find a and b.
            double a = (this->land[level][i].second - this->land[level][i-1].second)/(this->land[level][i].first - this->land[level][i-1].first);
            double b = this->land[level][i-1].second - a*this->land[level][i-1].first;

            double x1 = this->land[level][i-1].first;
            double x2 = this->land[level][i].first;

            //double first = b*(pow((x2-center),(double)(n+1))/(n+1)-pow((x1-center),(double)(n+1))/(n+1));
            //double second = a/(n+1)*((x2*pow((x2-center),(double)(n+1))) - (x1*pow((x1-center),(double)(n+1))) )
            //              +
            //              a/(n+1)*( pow((x2-center),(double)(n+2))/(n+2) - pow((x1-center),(double)(n+2))/(n+2) );
            //result += first;
            //result += second;

            double first = a/(n+2)*( pow( (x2-center) , (double)(n+2) ) - pow( (x1-center) , (double)(n+2) ) );
            double second = center/(n+1)*( pow( (x2-center) , (double)(n+1) ) - pow( (x1-center) , (double)(n+1) ) );
            double third = b/(n+1)*( pow( (x2-center) , (double)(n+1) ) - pow( (x1-center) , (double)(n+1) ) );

            if ( computeNthMomentDbg )
            {
	      std::cerr << "x1 : " << x1 << std::endl;
                std::cerr << "x2 : " << x2 << std::endl;
                std::cerr << "a : " << a << std::endl;
                std::cerr << "b : " << b << std::endl;
                std::cerr << "first : " << first << std::endl;
                std::cerr << "second : " << second << std::endl;
                std::cerr << "third : " << third << std::endl;
                getchar();
            }

            result += first + second + third;
        }
    }
    return result;
}//computeNthMoment

bool PersistenceLandscape::testLandscape( const PersistenceBarcodes& b )
{
    for ( size_t level = 0 ; level != this->land.size() ; ++level )
    {
        for ( size_t i = 1 ; i != this->land[level].size()-1 ; ++i )
        {
            if ( this->land[level][i].second < epsi )continue;
            //check if over this->land[level][i].first-this->land[level][i].second , this->land[level][i].first+this->land[level][i].second] there are level barcodes.
            unsigned nrOfOverlapping = 0;
            for ( size_t nr = 0 ; nr != b.barcodes.size() ; ++nr )
            {
                if ( ( b.barcodes[nr].first-epsi <= this->land[level][i].first-this->land[level][i].second )
                      &&
                      ( b.barcodes[nr].second+epsi >= this->land[level][i].first+this->land[level][i].second )
                   )
                {
                    ++nrOfOverlapping;
                }
            }
            if ( nrOfOverlapping != level+1 )
            {
                std::cout << "We have a problem : \n";
                std::cout << "this->land[level][i].first : " << this->land[level][i].first << "\n";
                std::cout << "this->land[level][i].second : " << this->land[level][i].second << "\n";
                std::cout << "[" << this->land[level][i].first-this->land[level][i].second << "," << this->land[level][i].first+this->land[level][i].second << "] \n";
                std::cout << "level : " << level << " , nrOfOverlapping: " << nrOfOverlapping << std::endl;
                getchar();
                for ( size_t nr = 0 ; nr != b.barcodes.size() ; ++nr )
                {
                    if ( ( b.barcodes[nr].first <= this->land[level][i].first-this->land[level][i].second )
                          &&
                          ( b.barcodes[nr].second >= this->land[level][i].first+this->land[level][i].second )
                       )
                    {
                        std::cout << "(" << b.barcodes[nr].first << "," << b.barcodes[nr].second << ")\n";
                    }
                    /*
                    std::cerr << "( b.barcodes[nr].first-epsi <= this->land[level][i].first-this->land[level][i].second ) : "<< ( b.barcodes[nr].first-epsi <= this->land[level][i].first-this->land[level][i].second ) << std::endl;
                    std::cerr << "( b.barcodes[nr].second+epsi >= this->land[level][i].first+this->land[level][i].second ) : " << ( b.barcodes[nr].second+epsi >= this->land[level][i].first+this->land[level][i].second ) << std::endl;
                    std::cerr << "( this->land[level][i].first-this->land[level][i].second ) " << ( this->land[level][i].first-this->land[level][i].second )  << std::endl;
                    std::cout << std::setprecision(20) << "We want : [" << this->land[level][i].first-this->land[level][i].second << "," << this->land[level][i].first+this->land[level][i].second << "] \n";
                    std::cout << "(" << b.barcodes[nr].first << "," << b.barcodes[nr].second << ")\n";
                    getchar();
                    */
                    //this->printToFiles("out");
                    //this->generateGnuplotCommandToPlot("out");
                    //getchar();getchar();getchar();
                }
            }
        }
    }
    return true;
}



bool computeLandscapeOnDiscreteSetOfPointsDBG = false;
void PersistenceLandscape::computeLandscapeOnDiscreteSetOfPoints( PersistenceBarcodes& b , double dx )
{
     std::pair<double,double> miMa = b.minMax();
     double bmin = miMa.first;
     double bmax = miMa.second;


     if(computeLandscapeOnDiscreteSetOfPointsDBG){std::cerr << "bmin: " << bmin << " , bmax :" << bmax << "\n";}

    //if(computeLandscapeOnDiscreteSetOfPointsDBG){}

     std::vector< std::pair<double,std::vector<double> > > result( (bmax-bmin)/(dx/2) + 2 );

     double x = bmin;
     int i = 0;
     while ( x <= bmax )
     {
         std::vector<double> v;
         result[i] = std::make_pair( x , v );
         x += dx/2.0;
         ++i;
     }

     if(computeLandscapeOnDiscreteSetOfPointsDBG){std::cerr << "Vector initally filled in \n";}


     for ( size_t i = 0 ; i != b.barcodes.size() ; ++i )
     {
         //adding barcode b.barcodes[i] to out mesh:
         double beginBar = b.barcodes[i].first;
         double endBar = b.barcodes[i].second;
         size_t index = ceil((beginBar-bmin)/(dx/2));
         while ( result[index].first < beginBar )++index;
         while ( result[index].first < beginBar )--index;
         double height = 0;
         //I know this is silly to add dx/100000 but this is neccesarry to make it work. Othervise, because of roundoff error, the program gave wrong results. It took me a while to track this.
         while (  height <= ((endBar-beginBar)/2.0) )
         {
             //go up
             result[index].second.push_back( height );
             height += dx/2;
             ++index;
         }
         height -= dx;
         while ( (height >= 0)  )
         {
             //std::cerr << "Next iteration\n";
             //go down
             result[index].second.push_back( height );
             height -= dx/2;
             ++index;
         }
     }

     //std::cerr << "All barcodes has been added to the mesh \n";

     unsigned indexOfLastNonzeroLandscape = 0;
     i = 0;
     for ( double x = bmin ; x <= bmax ; x = x+(dx/2) )
     {
         std::sort( result[i].second.begin() , result[i].second.end() , std::greater<double>() );
         if ( result[i].second.size() > indexOfLastNonzeroLandscape )indexOfLastNonzeroLandscape = result[i].second.size();
         ++i;
     }

     if ( computeLandscapeOnDiscreteSetOfPointsDBG ){std::cout << "Now we fill in the suitable vecors in this landscape \n";}
     std::vector< std::vector< std::pair<double,double> > > land(indexOfLastNonzeroLandscape);
     for ( unsigned dim = 0 ; dim != indexOfLastNonzeroLandscape ; ++dim )
     {
         land[dim].push_back( std::make_pair( INT_MIN,0 ) );
     }

     i = 0;
     for ( double x = bmin ; x <= bmax ; x = x+(dx/2) )
     {
         for ( size_t nr = 0 ; nr != result[i].second.size() ; ++nr )
         {
              land[nr].push_back(std::make_pair( result[i].first , result[i].second[nr] ));
         }
         ++i;
     }

     for ( unsigned dim = 0 ; dim != indexOfLastNonzeroLandscape ; ++dim )
     {
         land[dim].push_back( std::make_pair( INT_MAX,0 ) );
     }
     this->land.clear();
     this->land.swap(land);
     this->reduceAlignedPoints();
}



bool multiplyByIndicatorFunctionBDG = false;
PersistenceLandscape PersistenceLandscape::multiplyByIndicatorFunction( std::vector<std::pair<double,double> > indicator )const
{
    PersistenceLandscape result;
    for ( size_t dim = 0 ; dim != this->land.size() ; ++dim )
    {
        if(multiplyByIndicatorFunctionBDG){std::cout << "dim : " << dim << "\n";}
        std::vector< std::pair<double,double> > lambda_n;
        lambda_n.push_back( std::make_pair( 0 , INT_MIN ) );
        if ( indicator.size() > dim )
        {
            if (multiplyByIndicatorFunctionBDG)
            {
                std::cout << "There is nonzero indicator in this dimension\n";
                std::cout << "[ " << indicator[dim].first << " , " << indicator[dim].second << "] \n";
            }
            for ( size_t nr = 0 ; nr != this->land[dim].size() ; ++nr )
            {
                if (multiplyByIndicatorFunctionBDG){ std::cout << "this->land[dim][nr] : " << this->land[dim][nr].first << " , " << this->land[dim][nr].second << "\n";}
                if ( this->land[dim][nr].first < indicator[dim].first )
                {
                    if (multiplyByIndicatorFunctionBDG){std::cout << "Below treshold\n";}
                    continue;
                }
                if ( this->land[dim][nr].first > indicator[dim].second )
                {
                    if (multiplyByIndicatorFunctionBDG){std::cout << "Just pass above treshold \n";}
                    lambda_n.push_back( std::make_pair( indicator[dim].second , functionValue ( this->land[dim][nr-1] , this->land[dim][nr] , indicator[dim].second ) ) );
                    lambda_n.push_back( std::make_pair( indicator[dim].second , 0 ) );
                    break;
                }
                if ( (this->land[dim][nr].first >= indicator[dim].first) && (this->land[dim][nr-1].first <= indicator[dim].first) )
                {
                    if (multiplyByIndicatorFunctionBDG){std::cout << "Entering the indicator \n";}
                    lambda_n.push_back( std::make_pair( indicator[dim].first , 0 ) );
                    lambda_n.push_back( std::make_pair( indicator[dim].first , functionValue(this->land[dim][nr-1],this->land[dim][nr],indicator[dim].first) ) );
                }

                 if (multiplyByIndicatorFunctionBDG){std::cout << "We are here\n";}
                lambda_n.push_back( std::make_pair( this->land[dim][nr].first , this->land[dim][nr].second ) );
            }
        }
        lambda_n.push_back( std::make_pair( 0 , INT_MIN ) );
        if ( lambda_n.size() > 2 )
        {
            result.land.push_back( lambda_n );
        }
    }
    return result;
}


void PersistenceLandscape::printToFiles( const char* filename , unsigned from , unsigned to )const
{
    if ( from > to )throw("Error printToFiles printToFile( char* filename , unsigned from , unsigned to ). 'from' cannot be greater than 'to'.");
    //if ( to > this->land.size() )throw("Error in printToFiles( char* filename , unsigned from , unsigned to ). 'to' is out of range.");
    if ( to > this->land.size() ){to = this->land.size();}
    std::ofstream write;
    for ( size_t dim = from ; dim != to ; ++dim )
    {
        std::ostringstream name;
        name << filename << "_" << dim << ".dat";
        std::string fName = name.str();
        const char* FName = fName.c_str();

        write.open(FName);
        write << "#lambda_" << dim << std::endl;
        for ( size_t i = 1 ; i != this->land[dim].size()-1 ; ++i )
        {
            write << this->land[dim][i].first << "  " << this->land[dim][i].second << std::endl;
        }
        write.close();
    }
}


void PersistenceLandscape::printToFiles( const char* filename, int numberOfElementsLater ,  ... )const
{
  va_list arguments;
  va_start ( arguments, numberOfElementsLater );
  std::ofstream write;
  for ( int x = 0; x < numberOfElementsLater; x++ )
  {
       unsigned dim = va_arg ( arguments, unsigned );
       if ( dim > this->land.size() )throw("In function generateGnuplotCommandToPlot(char* filename,int numberOfElementsLater,  ... ), one of the number provided is greater than number of nonzero landscapes");
        std::ostringstream name;
       name << filename << "_" << dim << ".dat";
       std::string fName = name.str();
       const char* FName = fName.c_str();
       write.open(FName);
       write << "#lambda_" << dim << std::endl;
       for ( size_t i = 1 ; i != this->land[dim].size()-1 ; ++i )
       {
           write << this->land[dim][i].first << "  " << this->land[dim][i].second << std::endl;
       }
       write.close();
  }
  va_end ( arguments );
}


void PersistenceLandscape::printToFiles( const char* filename )const
{
    this->printToFiles(filename , (unsigned)0 , (unsigned)this->land.size() );
}

void PersistenceLandscape::printToFile( const char* filename , unsigned from , unsigned to )const
{
    if ( from > to )throw("Error in printToFile( char* filename , unsigned from , unsigned to ). 'from' cannot be greater than 'to'.");
    if ( to > this->land.size() )throw("Error in printToFile( char* filename , unsigned from , unsigned to ). 'to' is out of range.");
    std::ofstream write;
    write.open(filename);
    write << this->dimension << std::endl;
    for ( size_t dim = from ; dim != to ; ++dim )
    {
        write << "#lambda_" << dim << std::endl;
        for ( size_t i = 1 ; i != this->land[dim].size()-1 ; ++i )
        {
            write << this->land[dim][i].first << "  " << this->land[dim][i].second << std::endl;
        }
    }
    write.close();
}


void PersistenceLandscape::printToFile( const char* filename  )const
{
    this->printToFile(filename,0,this->land.size());
}


void PersistenceLandscape::generateGnuplotCommandToPlot( const char* filename, unsigned from , unsigned to )const
{
    if ( from > to )throw("Error in printToFile( char* filename , unsigned from , unsigned to ). 'from' cannot be greater than 'to'.");
    //if ( to > this->land.size() )throw("Error in printToFile( char* filename , unsigned from , unsigned to ). 'to' is out of range.");
    if ( to > this->land.size() ){to = this->land.size();}
    std::ostringstream result;
    result << "plot ";
    for ( size_t dim = from ; dim != to ; ++dim )
    {
        //result << "\"" << filename << "_" << dim <<".dat\" w lp".dat\" w lp title \"L" << dim <<"\"";
        result << "\"" << filename << "_" << dim <<".dat\" with lines notitle ";
        if ( dim != to-1 )
        {
            result << ", ";
        }
    }
    std::ofstream write;
    std::ostringstream outFile;
    outFile << filename << "_gnuplotCommand.txt";
    std::string outF = outFile.str();
    std::cout << "The gnuplot command can be found in the file \"" << outFile.str() << "\"\n";
    write.open(outF.c_str());
    write << result.str();
    write.close();
}

void PersistenceLandscape::generateGnuplotCommandToPlot(const char* filename,int numberOfElementsLater,  ... )const
{
   va_list arguments;
   va_start ( arguments, numberOfElementsLater );
   std::ostringstream result;
   result << "plot ";
   for ( int x = 0; x < numberOfElementsLater; x++ )
   {
        unsigned dim = va_arg ( arguments, unsigned );
        if ( dim > this->land.size() )throw("In function generateGnuplotCommandToPlot(char* filename,int numberOfElementsLater,  ... ), one of the number provided is greater than number of nonzero landscapes");
        result << "\"" << filename << "_" << dim <<".dat\" w lp title \"L" << dim <<"\"";
        if ( x != numberOfElementsLater-1 )
        {
            result << ", ";
        }
   }
   std::ofstream write;
   std::ostringstream outFile;
    outFile << filename << "_gnuplotCommand.txt";
    std::string outF = outFile.str();
    std::cout << "The gnuplot command can be found in the file \"" << outFile.str() << "\"\n";
    write.open(outF.c_str());
   write << result.str();
   write.close();
}


void PersistenceLandscape::generateGnuplotCommandToPlot( const char* filename )const
{
    this->generateGnuplotCommandToPlot( filename , (unsigned)0 , (unsigned)this->land.size() );
}


PersistenceLandscape::PersistenceLandscape(const PersistenceLandscape& oryginal)
{
    //std::cerr << "Running copy constructor \n";
    this->dimension = oryginal.dimension;
    std::vector< std::vector< std::pair<double,double> > > land( oryginal.land.size() );
    for ( size_t i = 0 ; i != oryginal.land.size() ; ++i )
    {
        land[i].insert( land[i].end() , oryginal.land[i].begin() , oryginal.land[i].end() );
    }
    //CHANGE
    //this->land = land;
    this->land.swap(land);
}

PersistenceLandscape PersistenceLandscape::operator=( const PersistenceLandscape& oryginal )
{
    this->dimension = oryginal.dimension;
    std::vector< std::vector< std::pair<double,double> > > land( oryginal.land.size() );
    for ( size_t i = 0 ; i != oryginal.land.size() ; ++i )
    {
        land[i].insert( land[i].end() , oryginal.land[i].begin() , oryginal.land[i].end() );
    }
    //CHANGE
    //this->land = land;
    this->land.swap(land);
    return *this;
}








/*
bool dbg = false;
PersistenceLandscape::PersistenceLandscape( const PersistenceBarcodes& p )
{
    this->dimension = p.dimensionOfBarcode;
    std::vector< std::pair<double,double> > characteristicPoints(p.barcodes.size());
    for ( size_t i = 0 ; i != p.barcodes.size() ; ++i )
    {
        characteristicPoints[i] = std::make_pair((p.barcodes[i].first+p.barcodes[i].second)/2.0 , (p.barcodes[i].second - p.barcodes[i].first)/2.0) ;
    }
    std::sort( characteristicPoints.begin() , characteristicPoints.end() , comparePoints );



    while ( !characteristicPoints.empty() )
    {
        if ( dbg )
        {
            std::cerr << "Characteristic points at the very beginning :\n";
            for ( size_t aa = 0 ; aa != characteristicPoints.size() ; ++aa )
            {
                std::cerr << "(" << characteristicPoints[aa] << ") , ";
            }
            std::cerr << "\n";
        }


        std::vector< std::pair<double,double> > lambda_n;
        lambda_n.push_back( std::make_pair( INT_MIN , 0 ) );
        lambda_n.push_back( std::make_pair(birth(characteristicPoints[0]),0) );
        lambda_n.push_back( characteristicPoints[0] );
        if ( dbg )
        {
            std::cout << "Adding : " << std::make_pair( INT_MIN , 0 ) << " to lambda_n \n";
            std::cout << "Adding : " << std::make_pair(birth(characteristicPoints[0]),0) << " to lambda_n \n";
            std::cout << "Adding : " << characteristicPoints[0] << " to lambda_n \n";
        }

        size_t q = 1;

        std::list< std::pair<double,double> > newCharacteristicPoints;
        std::list< std::pair<double,double> >::iterator pos = newCharacteristicPoints.end();
        while ( q <= characteristicPoints.size()-1 )
        {
            size_t p = 0;
            if ( dbg ){std::cout << "characteristicPoints[q] : " << characteristicPoints[q] << "\n";std::cin.ignore();}
            while ( ( q<characteristicPoints.size() ) && ( death(characteristicPoints[q]) <= death( lambda_n[lambda_n.size()-1] ) ) )
            {
                if ( dbg ){std::cout << "Rewriting new characteristic point : " << characteristicPoints[q] << "\n";}
                newCharacteristicPoints.push_back( characteristicPoints[q] );
                ++q;
            }

            if ( q < characteristicPoints.size() )
            {
                if ( birth(characteristicPoints[q]) <= death(lambda_n[lambda_n.size()-1]) )
                {
                    std::pair<double,double> pair =   std::make_pair(
                                                       0.5*(birth(characteristicPoints[q])+death(lambda_n[lambda_n.size()-1]))
                                                       ,
                                                       0.5*((death(lambda_n[lambda_n.size()-1]) - birth(characteristicPoints[q])) )
                                                      );
                    if ( dbg ){std::cout << "Adding : " << pair << " to lambda_n\n";}


                    p = q+1;
                    if ( dbg )
                    {
                        std::cerr << "Jestesmy zaraz przed petla \n";std::cin.ignore();
                        std::cerr << "(p < characteristicPoints.size() ) : " << (p < characteristicPoints.size() ) << "\n";
                        std::cerr << "!comparePoints(characteristicPoints[p],pair) : " << comparePoints(characteristicPoints[p],pair) << "\n";
                    }
                    while ( (p < characteristicPoints.size() ) && comparePoints(characteristicPoints[p],pair) )
                    {
                        if ( dbg )std::cout << "Adding new characteristic point in while loop: " << characteristicPoints[p] << "\n";
                        newCharacteristicPoints.push_back( characteristicPoints[p] );
                        ++p;
                    }
                    if ( dbg )std::cout << "Adding new characteristic point: " << pair << "\n";
                    newCharacteristicPoints.push_back( pair );
                    lambda_n.push_back( pair );
                }
                else
                {
                    lambda_n.push_back( std::make_pair( death(lambda_n[lambda_n.size()-1]) , 0 ) );
                    lambda_n.push_back( std::make_pair( birth(characteristicPoints[q]) , 0 ) );
                    p = 1;
                    if ( dbg )std::cout << "Aadding : (" << death(lambda_n[lambda_n.size()-1]) << ", 0 ) to lambda_n \n";
                    if ( dbg )std::cout << "Aadding : (" << birth(characteristicPoints[q]) << ", 0 ) to lambda_n \n";
                }

                 if ( dbg )std::cout << "Adding at the end of while : (" << characteristicPoints[q] << ") to lambda_n \n";
                 lambda_n.push_back( characteristicPoints[q] );
                 q += p;

                 if ( dbg )std::cin.ignore();
            }
        }

        characteristicPoints.clear();
        characteristicPoints.insert( characteristicPoints.end() , newCharacteristicPoints.begin() , newCharacteristicPoints.end() );

        if ( dbg )
        {
            std::cerr << "newCharacteristicPoints : \n";
            for ( std::vector< std::pair<double,double> >::iterator it = characteristicPoints.begin() ; it != characteristicPoints.end() ; ++it )
            {
                std::cerr << "(" << *it << ")  ";
            }
            std::cerr << "\n\n";
        }


        lambda_n.push_back( std::make_pair(death(lambda_n[lambda_n.size()-1]),0) );
        if ( dbg )std::cout << "Adding : " << std::make_pair(death(lambda_n[lambda_n.size()-1]),0) << " to lambda_n \n";

        lambda_n.push_back( std::make_pair( INT_MAX , 0 ) );

        if ( dbg )
        {
            std::cout << "Adding : " << std::make_pair( INT_MAX , 0 ) << " to lambda_n \n";
            std::cout << "That is a new iteration of while \n\n\n\n";
            std::cin.ignore();
        }


        lambda_n.erase(std::unique(lambda_n.begin(), lambda_n.end()), lambda_n.end());
        this->land.push_back( lambda_n );
    }
}
*/


//TODO -- removewhen the problem is respved
bool check( unsigned i , std::vector< std::pair<double,double> > v )
{
    if ( (i < 0) || (i >= v.size()) )
    {
        std::cout << "you want to get to index : " << i << " while there are only  : " << v.size() << " indices \n";
        std::cin.ignore();
        return true;
    }
    return false;
}
//if ( check( , ) ){std::cerr << "OUT OF MEMORY \n";}



PersistenceLandscape::PersistenceLandscape( const PersistenceBarcodes& p )
{
    bool dbg = false;
    if ( dbg ){std::cerr << "PersistenceLandscape::PersistenceLandscape( const PersistenceBarcodes& p )" << std::endl;}
    if ( !useGridInComputations )
    {
      if ( dbg ){std::cerr << "PL version" << std::endl;getchar();}
        //this is a general algorithm to construct persistence landscapes.
        this->dimension = p.dimensionOfBarcode;
        std::vector< std::pair<double,double> > bars;
        bars.insert( bars.begin() , p.barcodes.begin() , p.barcodes.end() );
        std::sort( bars.begin() , bars.end() , comparePoints2 );

        if (dbg)
        {
            std::cerr << "Bars : \n";
            for ( size_t i = 0 ; i != bars.size() ; ++i )
            {
                std::cerr << bars[i] << "\n";
            }
            getchar();
        }

        std::vector< std::pair<double,double> > characteristicPoints(p.barcodes.size());
        for ( size_t i = 0 ; i != bars.size() ; ++i )
        {
            characteristicPoints[i] = std::make_pair((bars[i].first+bars[i].second)/2.0 , (bars[i].second - bars[i].first)/2.0);
        }
        std::vector< std::vector< std::pair<double,double> > > persistenceLandscape;
        while ( !characteristicPoints.empty() )
        {
            if(dbg)
            {
                for ( size_t i = 0 ; i != characteristicPoints.size() ; ++i )
                {
                    std::cout << "("  << characteristicPoints[i] << ")\n";
                }
                std::cin.ignore();
            }

            std::vector< std::pair<double,double> > lambda_n;
            lambda_n.push_back( std::make_pair( INT_MIN , 0 ) );
            lambda_n.push_back( std::make_pair(birth(characteristicPoints[0]),0) );
            lambda_n.push_back( characteristicPoints[0] );

            if (dbg)
            {
                std::cerr << "1 Adding to lambda_n : (" << std::make_pair( INT_MIN , 0 ) << ") , (" << std::make_pair(birth(characteristicPoints[0]),0) << ") , (" << characteristicPoints[0] << ") \n";
            }

            int i = 1;
            std::vector< std::pair<double,double> >  newCharacteristicPoints;
            while ( i < characteristicPoints.size() )
            {
                size_t p = 1;
                if ( (birth(characteristicPoints[i]) >= birth(lambda_n[lambda_n.size()-1])) && (death(characteristicPoints[i]) > death(lambda_n[lambda_n.size()-1])) )
                {
                    if ( birth(characteristicPoints[i]) < death(lambda_n[lambda_n.size()-1]) )
                    {
                        std::pair<double,double> point = std::make_pair( (birth(characteristicPoints[i])+death(lambda_n[lambda_n.size()-1]))/2 , (death(lambda_n[lambda_n.size()-1])-birth(characteristicPoints[i]))/2 );
                        lambda_n.push_back( point );
                        if (dbg)
                        {
                            std::cerr << "2 Adding to lambda_n : (" << point << ")\n";
                        }


                        if ( dbg )
                        {
                            std::cerr << "comparePoints(point,characteristicPoints[i+p]) : " << comparePoints(point,characteristicPoints[i+p]) << "\n";
                            std::cerr << "characteristicPoints[i+p] : " << characteristicPoints[i+p] << "\n";
                            std::cerr << "point : " << point << "\n";
                            getchar();
                        }


                        /*
                        while ( (i+p < characteristicPoints.size() ) && (comparePoints(point,characteristicPoints[i+p])) && ( death(point) >= death(characteristicPoints[i+p]) ) )
                        {
                            newCharacteristicPoints.push_back( characteristicPoints[i+p] );
                            if (dbg)
                            {
                                std::cerr << "characteristicPoints[i+p] : " << characteristicPoints[i+p] << "\n";
                                std::cerr << "point : " << point << "\n";
                                std::cerr << "comparePoints(point,characteristicPoints[i+p]) : " << comparePoints(point,characteristicPoints[i+p]) << std::endl;
                                std::cerr << "characteristicPoints[i+p] birth and death : " << birth(characteristicPoints[i+p]) << " , " << death(characteristicPoints[i+p]) << "\n";
                                std::cerr << "point birth and death : " << birth(point) << " , " << death(point) << "\n";

                                std::cerr << "3 Adding to newCharacteristicPoints : (" << characteristicPoints[i+p] << ")\n";
                                getchar();
                            }
                            ++p;
                        }
                        */
                        while ( (i+p < characteristicPoints.size() ) && ( almostEqual(birth(point),birth(characteristicPoints[i+p])) ) && ( death(point) <= death(characteristicPoints[i+p]) ) )
                        {
                            newCharacteristicPoints.push_back( characteristicPoints[i+p] );
                            if (dbg)
                            {
                                std::cerr << "3.5 Adding to newCharacteristicPoints : (" << characteristicPoints[i+p] << ")\n";
                                getchar();
                            }
                            ++p;
                        }


                        newCharacteristicPoints.push_back( point );
                        if (dbg)
                        {
                            std::cerr << "4 Adding to newCharacteristicPoints : (" << point << ")\n";
                        }


                        while ( (i+p < characteristicPoints.size() ) && ( birth(point) <= birth(characteristicPoints[i+p]) ) && (death(point)>=death(characteristicPoints[i+p])) )
                        {
                            newCharacteristicPoints.push_back( characteristicPoints[i+p] );
                            if (dbg)
                            {
                                std::cerr << "characteristicPoints[i+p] : " << characteristicPoints[i+p] << "\n";
                                std::cerr << "point : " << point << "\n";
                                std::cerr << "comparePoints(point,characteristicPoints[i+p]) : " << comparePoints(point,characteristicPoints[i+p]) << std::endl;
                                std::cerr << "characteristicPoints[i+p] birth and death : " << birth(characteristicPoints[i+p]) << " , " << death(characteristicPoints[i+p]) << "\n";
                                std::cerr << "point birth and death : " << birth(point) << " , " << death(point) << "\n";

                                std::cerr << "3 Adding to newCharacteristicPoints : (" << characteristicPoints[i+p] << ")\n";
                                getchar();
                            }
                            ++p;
                        }

                    }
                    else
                    {
                        lambda_n.push_back( std::make_pair( death(lambda_n[lambda_n.size()-1]) , 0 ) );
                        lambda_n.push_back( std::make_pair( birth(characteristicPoints[i]) , 0 ) );
                        if (dbg)
                        {
                            std::cerr << "5 Adding to lambda_n : (" << std::make_pair( death(lambda_n[lambda_n.size()-1]) , 0 ) << ")\n";
                            std::cerr << "5 Adding to lambda_n : (" << std::make_pair( birth(characteristicPoints[i]) , 0 ) << ")\n";
                        }
                    }
                    lambda_n.push_back( characteristicPoints[i] );
                    if (dbg)
                    {
                        std::cerr << "6 Adding to lambda_n : (" << characteristicPoints[i] << ")\n";
                    }
                }
                else
                {
                    newCharacteristicPoints.push_back( characteristicPoints[i] );
                    if (dbg)
                    {
                        std::cerr << "7 Adding to newCharacteristicPoints : (" << characteristicPoints[i] << ")\n";
                    }
                }
                i = i+p;
            }
            lambda_n.push_back( std::make_pair(death(lambda_n[lambda_n.size()-1]),0) );
            lambda_n.push_back( std::make_pair( INT_MAX , 0 ) );

            //CHANGE
            characteristicPoints = newCharacteristicPoints;
            //characteristicPoints.swap(newCharacteristicPoints);

            lambda_n.erase(std::unique(lambda_n.begin(), lambda_n.end()), lambda_n.end());
            this->land.push_back( lambda_n );
        }
    }
    else
    {
      if ( dbg ){std::cerr << "Constructing persistence landscape based on a grid \n";getchar();}
        //in this case useGridInComputations is true, therefore we will build a landscape on a grid.
        extern double gridDiameter;
        this->dimension = p.dimensionOfBarcode;
        std::pair<double,double> minMax = p.minMax();
        size_t numberOfBins = 2*((minMax.second - minMax.first)/gridDiameter)+1;

        //first element of a pair std::pair< double , std::vector<double> > is a x-value. Second element is a vector of values of landscapes.
        std::vector< std::pair< double , std::vector<double> > > criticalValuesOnPointsOfGrid(numberOfBins);
        //filling up the bins:

        //Now, the idea is to iterate on this->land[lambda-1] and use only points over there. The problem is at the very beginning, when there is nothing
        //in this->land. That is why over here, we make a fate this->land[0]. It will be later deteted before moving on.
        std::vector< std::pair<double,double> > aa;
        aa.push_back( std::make_pair( INT_MIN , 0 ) );
        double x = minMax.first;
        for ( size_t i = 0 ; i != numberOfBins ; ++i )
        {
            std::vector<double> v;
            std::pair< double , std::vector<double> > p = std::make_pair( x , v );
            aa.push_back( std::make_pair( x , 0 ) );
            criticalValuesOnPointsOfGrid[i] = p;
            if ( dbg ){std::cerr << "x : " << x << std::endl;}
            x += 0.5*gridDiameter;
        }
        aa.push_back( std::make_pair( INT_MAX , 0 ) );

        if ( dbg ){std::cerr << "Grid has been created. Now, begin to add intervals \n";}

        //for every peristent interval
        for ( size_t intervalNo = 0 ; intervalNo != p.size() ; ++intervalNo )
        {
            size_t beginn = (size_t)(2*( p.barcodes[intervalNo].first-minMax.first )/( gridDiameter ))+1;
            if ( dbg ){std::cerr << "We are considering interval : [" << p.barcodes[intervalNo].first << "," << p.barcodes[intervalNo].second << "]. It will begin in  : " << beginn << " in the grid \n";}
            while ( criticalValuesOnPointsOfGrid[beginn].first < p.barcodes[intervalNo].second )
            {
                if ( dbg )
                {
		  std::cerr << "Adding a value : (" << criticalValuesOnPointsOfGrid[beginn].first << "," << std::min( fabs(criticalValuesOnPointsOfGrid[beginn].first-p.barcodes[intervalNo].first) ,fabs(criticalValuesOnPointsOfGrid[beginn].first-p.barcodes[intervalNo].second) ) << ") " << std::endl;
                }
                criticalValuesOnPointsOfGrid[beginn].second.push_back(std::min( fabs(criticalValuesOnPointsOfGrid[beginn].first-p.barcodes[intervalNo].first) ,fabs(criticalValuesOnPointsOfGrid[beginn].first-p.barcodes[intervalNo].second) ) );
                ++beginn;
            }
        }

        //now, the basic structure is created. We need to translate it to a persistence landscape data structure.
        //To do so, first we need to sort all the vectors in criticalValuesOnPointsOfGrid[i].second
        size_t maxNonzeroLambda = 0;
        for ( size_t i = 0 ; i != criticalValuesOnPointsOfGrid.size() ; ++i )
        {
            std::sort( criticalValuesOnPointsOfGrid[i].second.begin() , criticalValuesOnPointsOfGrid[i].second.end() , std::greater<int>() );
            if ( criticalValuesOnPointsOfGrid[i].second.size() > maxNonzeroLambda ){maxNonzeroLambda = criticalValuesOnPointsOfGrid[i].second.size();}
        }
        if ( dbg )
        {
	  std::cerr << "After sorting \n";
            for ( size_t i = 0 ; i != criticalValuesOnPointsOfGrid.size() ; ++i )
            {
	      std::cerr << "x : " << criticalValuesOnPointsOfGrid[i].first << " : ";
                for ( size_t j = 0 ; j != criticalValuesOnPointsOfGrid[i].second.size() ; ++j )
                {
		  std::cerr << criticalValuesOnPointsOfGrid[i].second[j] << " ";
                }
		std::cerr << "\n\n";
            }
        }

        this->land.push_back(aa);
        for ( size_t lambda = 0 ; lambda != maxNonzeroLambda ; ++lambda )
        {
	  if ( dbg ){std::cerr << "Constructing lambda_" << lambda << std::endl;}
            std::vector< std::pair<double,double> >  nextLambbda;
            nextLambbda.push_back( std::make_pair(INT_MIN,0) );
            //for every element in the domain for which the previous landscape is nonzero.
            bool wasPrevoiusStepZero = true;
            size_t nr = 1;
            while (  nr < this->land[ this->land.size()-1 ].size()-1 )
            {
	      if (dbg) std::cerr << "nr : " << nr << std::endl;
                size_t address = (size_t)(2*( this->land[ this->land.size()-1 ][nr].first-minMax.first )/( gridDiameter ));
                if ( dbg )
                {
		  std::cerr << "We are considering the element x : " << this->land[ this->land.size()-1 ][nr].first << ". Its position in the structure is : " << address << std::endl;
                }

                if (  criticalValuesOnPointsOfGrid[address].second.size() <= lambda  )
                {
                    if (!wasPrevoiusStepZero)
                    {
                        wasPrevoiusStepZero = true;
                        if ( dbg ){std::cerr << "AAAdding : (" << criticalValuesOnPointsOfGrid[address].first << " , " << 0 << ") to lambda_" << lambda << std::endl;getchar();}
                        nextLambbda.push_back( std::make_pair( criticalValuesOnPointsOfGrid[address].first , 0 ) );
                    }
                }
                else
                {
                     if ( wasPrevoiusStepZero )
                     {
		       if ( dbg ){std::cerr << "Adding : (" << criticalValuesOnPointsOfGrid[address-1].first << " , " << 0 << ") to lambda_" << lambda << std::endl;getchar();}
                         nextLambbda.push_back( std::make_pair( criticalValuesOnPointsOfGrid[address-1].first , 0 ) );
                         wasPrevoiusStepZero = false;
                     }

                     if ( dbg ){std::cerr << "AAdding : (" << criticalValuesOnPointsOfGrid[address].first << " , " << criticalValuesOnPointsOfGrid[address].second[lambda] << ") to lambda_" << lambda << std::endl;getchar();}
                     nextLambbda.push_back( std::make_pair( criticalValuesOnPointsOfGrid[address].first , criticalValuesOnPointsOfGrid[address].second[lambda] ) );
                }
                ++nr;
            }
            if ( dbg ){std::cerr << "Done with : lambda_" << lambda << std::endl;getchar();getchar();getchar();}
            if ( lambda == 0 )
            {
                //removing the first, fake, landscape
                this->land.clear();
            }
            nextLambbda.push_back( std::make_pair(INT_MAX,0) );
            nextLambbda.erase( unique( nextLambbda.begin(), nextLambbda.end() ), nextLambbda.end() );
            this->land.push_back( nextLambbda );
        }
    }
}


/*

        //and now it remains to fill in the structure of the peristence landscape:
        //We are using this extra structure for the following reason: in the naive algorithm we would have to iterate through the whole criticalValuesOnPointsOfGrid
        //as many times as there are nonzero lambda_n's. But we know that the support of lambda_n contains support of lambda_{n+1}. So, when we already know that the
        //domain of lambda_n is very restricted, there is no need to look for lambda_{n+1} outside of this domain. That is why we need those bounds for the support of the
        //previous landscape function.
        cerr << "HereAA \n";getchar();

        std::vector<double> placesWherePreviousLandscapeIsNonzero;
        for ( size_t i = 0 ; i != criticalValuesOnPointsOfGrid.size() ; ++i )
        {
            if ( (criticalValuesOnPointsOfGrid[i].second.size() ) && (criticalValuesOnPointsOfGrid[i].second[0] == 0.5) )
            {
                if ( dbg ){cerr << "Found a place, where lambda_0 became nonzero : " << i << endl;}
                placesWherePreviousLandscapeIsNonzero.push_back( i );
                //if at the next step it again became zero, we need to duplicate this point in the placesWherePreviousLandscapeIsNonzero vector.
                if ( criticalValuesOnPointsOfGrid[i+1].second.size() == 0 )
                {
                    placesWherePreviousLandscapeIsNonzero.push_back( i );
                }
            }
        }

        cerr << "Here \n";getchar();


        //std::vector< std::vector< std::pair<double,double> > > land;
        for ( size_t level = 0 ; level != maxNonzeroLambda ; ++level )
        {

            if ( dbg )
            {
                cerr << "placesWherePreviousLandscapeIsNonzero.size() : " << placesWherePreviousLandscapeIsNonzero.size() << endl;
                cerr << "placesWherePreviousLandscapeIsNonzero : \n";
                for ( size_t i = 0 ; i != placesWherePreviousLandscapeIsNonzero.size() ; ++i )
                {
                    cerr << placesWherePreviousLandscapeIsNonzero[i] << " ";
                }
                cerr << endl;
                getchar();
            }
            cerr << "maxNonzeroLambda : " << maxNonzeroLambda << endl;//aaa

            std::vector<double> newPlacesWherePreviousLandscapeIsNonzero;
            if ( dbg ){cerr << "Begin construction of lambda_" << level << endl;}

            std::vector< std::pair<double,double> > lambdaLevel;
            lambdaLevel.push_back( std::make_pair(INT_MIN,0) );
            //construct lambda_level. We should do it in a smart way...

            for ( size_t j = 0 ; j <= placesWherePreviousLandscapeIsNonzero.size()-1 ; j+=2 )
            {
                if (dbg)cerr << "j : " << j << endl;
                size_t k = placesWherePreviousLandscapeIsNonzero[j];
                while ( k <= placesWherePreviousLandscapeIsNonzero[j+1] )
                {
                    if (dbg)cerr << "k : " << k << endl;
                    if (dbg)cerr << "placesWherePreviousLandscapeIsNonzero[j+1] : " << placesWherePreviousLandscapeIsNonzero[j+1] << endl;
                    cerr << "criticalValuesOnPointsOfGrid[k].second.size() : " << criticalValuesOnPointsOfGrid[k].second.size() << endl;
                    bool wasCriticalValueAtZeroAdded = false;
                    if ( criticalValuesOnPointsOfGrid[k].second.size() > level )
                    {
                        if ( criticalValuesOnPointsOfGrid[k].second[level] == 0.5 )
                        {
                            //in this case we need to add a critical point at zero before or after this critical point.
                            if ( lambdaLevel.size() == 1 )
                            {
                                //this is the first point, we need to add zero critical point
                                lambdaLevel.push_back( std::make_pair( criticalValuesOnPointsOfGrid[k].first-gridDiameter/2 , 0 ) );
                                if ( dbg ){cerr << "Adding : (" << criticalValuesOnPointsOfGrid[k].first-gridDiameter/2 << "," << 0<< ")" << endl;}
                                wasCriticalValueAtZeroAdded = true;
                            }
                            else
                            {
                                //we know that lambdaLevel.size() is always > 1.
                                if ( lambdaLevel[lambdaLevel.size()-1].second == 0 )
                                {
                                    //new connected component of the support just begins
                                    lambdaLevel.push_back( std::make_pair( criticalValuesOnPointsOfGrid[k].first-gridDiameter/2 , 0 ) );
                                    if ( dbg ){cerr << "AAAdding : (" << criticalValuesOnPointsOfGrid[k].first-gridDiameter/2 << "," << 0<< ")" << endl;}
                                    wasCriticalValueAtZeroAdded = true;
                                }
                            }
                        }
                        lambdaLevel.push_back( std::make_pair( criticalValuesOnPointsOfGrid[k].first , criticalValuesOnPointsOfGrid[k].second[level] ) );
                        if ( dbg ){cerr << "Level : " << level << " adding a critical point : (" << criticalValuesOnPointsOfGrid[k].first << "," <<criticalValuesOnPointsOfGrid[k].second[level] << ")\n";getchar();}
                        getchar();

                        if ( criticalValuesOnPointsOfGrid[k].second[level] == 0.5 )
                        {
                            //cerr << "newPlacesWherePreviousLandscapeIsNonzero.push_back(" << k << ") \n";
                            newPlacesWherePreviousLandscapeIsNonzero.push_back(k);
                            if ( wasCriticalValueAtZeroAdded )
                            {
                                //if the critical value (x,0) was not added before this point, it have to be added after it.
                                lambdaLevel.push_back( std::make_pair( criticalValuesOnPointsOfGrid[k].first+gridDiameter/2 , 0 ) );
                                if ( dbg ){cerr << "Adding : (" << criticalValuesOnPointsOfGrid[k].first+gridDiameter/2 << "," << 0<< ")" << endl;}
                            }
                        }
                    }
                    ++k;
                }
            }
            placesWherePreviousLandscapeIsNonzero.swap( newPlacesWherePreviousLandscapeIsNonzero );
            if ( dbg ){cerr << "Adding the closing point : (" << INT_MAX << " , " << 0 << ")" << endl;}
            lambdaLevel.push_back( std::make_pair(INT_MAX,0) );
            this->land.push_back( lambdaLevel );
        }
*/

/*
bool dbg = false;
PersistenceLandscape::PersistenceLandscape( const PersistenceBarcodes& p )
{
    if (dbg)
    {
        std::cerr << "PersistenceLandscape::PersistenceLandscape( const PersistenceBarcodes& p ) \n";
        std::cerr << "p.barcodes.size() : " << p.barcodes.size() << "\n";
    }

    this->dimension = p.dimensionOfBarcode;
    std::vector< std::pair<double,double> > characteristicPoints(p.barcodes.size());
    for ( size_t i = 0 ; i != p.barcodes.size() ; ++i )
    {
        characteristicPoints[i] = std::make_pair((p.barcodes[i].first+p.barcodes[i].second)/2.0 , (p.barcodes[i].second - p.barcodes[i].first)/2.0) ;
    }
    if (dbg)std::cerr << "Soering\n";
    std::sort( characteristicPoints.begin() , characteristicPoints.end() , comparePoints );

    std::vector< std::vector< std::pair<double,double> > > persistenceLandscape;
    while ( !characteristicPoints.empty() )
    {
        if (dbg)std::cerr << "Next iteration of the while loop \n";
        if (dbg)
        {
            std::cerr << "characteristicPoints.size() : " << characteristicPoints.size() << "\n";
            std::cerr << "Characteristic points : \n";
            for ( size_t i = 0 ; i != characteristicPoints.size() ; ++i )
            {
                std::cout << characteristicPoints[i].first << "," << characteristicPoints[i].second << "\n";
            }
            //std::cin.ignore();
        }


        std::vector< std::pair<double,double> > lambda_n;
        lambda_n.push_back( std::make_pair( INT_MIN , 0 ) );
        lambda_n.push_back( std::make_pair(birth(characteristicPoints[0]),0) );
        lambda_n.push_back( characteristicPoints[0] );
        if (dbg)std::cerr << "Adding to lambda_n : " << std::make_pair( INT_MIN , 0 ) << "\n";
        if (dbg)std::cerr << "Adding to lambda_n : " << std::make_pair(birth(characteristicPoints[0]),0) << "\n";
        if (dbg)std::cerr << "Adding to lambda_n : " << characteristicPoints[0] << "\n";


        int i = 1;

        if (dbg)std::cerr << "First characteristic point: " << characteristicPoints[0].first << " , " << characteristicPoints[0].second << std::endl;

        std::list< std::pair<double,double> >  newCharacteristicPoints;
        while ( i != characteristicPoints.size() )
        {
            size_t p = 1;
            if (dbg)std::cerr << "i : " << i << std::endl;
            //(death(characteristicPoints[i]) >= death(lambda_n[lambda_n.size()-1]))
            if ( (birth(characteristicPoints[i]) > birth(lambda_n[lambda_n.size()-1])) && (death(characteristicPoints[i]) > death(lambda_n[lambda_n.size()-1])) )
            {
                if (dbg)std::cerr << "I have found the next characteristic point : " << characteristicPoints[i].first << " , " << characteristicPoints[i].second << std::endl;
                if ( birth(characteristicPoints[i]) < death(lambda_n[lambda_n.size()-1]) )
                {
                    if (dbg)std::cerr << "Creation of a new characteristic point  :" << (birth(characteristicPoints[i])+death(lambda_n[lambda_n.size()-1]))/2 << " , " << (death(lambda_n[lambda_n.size()-1])-birth(characteristicPoints[i]))/2 << std::endl;

                    std::pair<double,double> point = std::make_pair( (birth(characteristicPoints[i])+death(lambda_n[lambda_n.size()-1]))/2 , (death(lambda_n[lambda_n.size()-1])-birth(characteristicPoints[i]))/2 );

                    if ( dbg )std::cout << "lambda_n ass : " << std::make_pair( (birth(characteristicPoints[i])+death(lambda_n[lambda_n.size()-1]))/2 , (death(lambda_n[lambda_n.size()-1])-birth(characteristicPoints[i]))/2 ) << "\n";
                    lambda_n.push_back( std::make_pair( (birth(characteristicPoints[i])+death(lambda_n[lambda_n.size()-1]))/2 , (death(lambda_n[lambda_n.size()-1])-birth(characteristicPoints[i]))/2 ) );

                    if ( dbg )
                    {
                        std::cerr << "Jestesmy zaraz przed petla \n";//std::cin.ignore();
                        std::cerr << "(p < characteristicPoints.size() ) : " << (p < characteristicPoints.size() ) << "\n";
                        std::cerr << "!comparePoints(characteristicPoints[p],point) : " << comparePoints(characteristicPoints[p],point) << "\n";
                    }
                    while ( (i+p < characteristicPoints.size() ) && comparePoints(characteristicPoints[i+p],point) )
                    {
                        if ( dbg )std::cout << "Adding new characteristic point in while loop: " << characteristicPoints[i+p] << "\n";
                        newCharacteristicPoints.push_back( characteristicPoints[i+p] );
                        ++p;
                    }
                    newCharacteristicPoints.push_back( point );
                }
                else
                {
                    lambda_n.push_back( std::make_pair( death(lambda_n[lambda_n.size()-1]) , 0 ) );
                    lambda_n.push_back( std::make_pair( birth(characteristicPoints[i]) , 0 ) );

                    if (dbg)std::cout << "lamnda_n adding : " << std::make_pair( death(lambda_n[lambda_n.size()-1]) , 0 ) << "\n";
                    if (dbg)std::cout << "lamnda_n adding : " << std::make_pair( birth(characteristicPoints[i]) , 0 ) << "\n";
                }
                if (dbg)std::cout << "lamnda_n adding : " << characteristicPoints[i] << "\n";
                lambda_n.push_back( characteristicPoints[i] );
            }
            else
            {
                if (dbg)
                {
                        std::cerr << "Writing new point as newCharacteristicPoints : " << characteristicPoints[i].first << " , " << characteristicPoints[i].second << std::endl;//std::cin.ignore();
                }
                newCharacteristicPoints.push_back( characteristicPoints[i] );
            }
            i = i+p;
        }
        lambda_n.push_back( std::make_pair(death(lambda_n[lambda_n.size()-1]),0) );
        lambda_n.push_back( std::make_pair( INT_MAX , 0 ) );

        //std::cerr << "Lamnda_" << this->land.size() << " has been created\n";

        if ( dbg )
        {
            std::cerr << "lambda_" << persistenceLandscape.size() << ": \n";
            for ( size_t aa = 0  ; aa != lambda_n.size() ; ++aa )
            {
                std::cerr << lambda_n[aa].first << " , " << lambda_n[aa].second << std::endl;
            }
        }
        //CHANGE
        //characteristicPoints = newCharacteristicPoints;
        characteristicPoints.clear();
        characteristicPoints.insert( characteristicPoints.begin() , newCharacteristicPoints.begin() , newCharacteristicPoints.end() );

        lambda_n.erase(std::unique(lambda_n.begin(), lambda_n.end()), lambda_n.end());
        this->land.push_back( lambda_n );
    }
}

*/




/*
PersistenceLandscape::PersistenceLandscape( const PersistenceBarcodes& p )
{
    this->dimension = p.dimensionOfBarcode;
    std::vector< std::pair<double,double> > characteristicPoints(p.barcodes.size());
    for ( size_t i = 0 ; i != p.barcodes.size() ; ++i )
    {
        characteristicPoints[i] = std::make_pair((p.barcodes[i].first+p.barcodes[i].second)/2.0 , (p.barcodes[i].second - p.barcodes[i].first)/2.0) ;
    }
    std::sort( characteristicPoints.begin() , characteristicPoints.end() , comparePoints );
    std::vector< std::vector< std::pair<double,double> > > persistenceLandscape;
    while ( !characteristicPoints.empty() )
    {
        std::vector< std::pair<double,double> > lambda_n;
        lambda_n.push_back( std::make_pair( INT_MIN , 0 ) );
        lambda_n.push_back( std::make_pair(birth(characteristicPoints[0]),0) );
        lambda_n.push_back( characteristicPoints[0] );
        int i = 1;
        std::vector< std::pair<double,double> >  newCharacteristicPoints;
        while ( i != characteristicPoints.size() )
        {
            //(death(characteristicPoints[i]) >= death(lambda_n[lambda_n.size()-1]))
            if ( (birth(characteristicPoints[i]) > birth(lambda_n[lambda_n.size()-1])) && (death(characteristicPoints[i]) >= death(lambda_n[lambda_n.size()-1])) )
            {
                if ( birth(characteristicPoints[i]) < death(lambda_n[lambda_n.size()-1]) )
                {
                    newCharacteristicPoints.push_back( std::make_pair(
                                                                      (birth(characteristicPoints[i])+death(lambda_n[lambda_n.size()-1]))/2 ,
                                                                      (death(lambda_n[lambda_n.size()-1])-birth(characteristicPoints[i]))/2
                                                                      )
                                                      );
                    lambda_n.push_back( std::make_pair( (birth(characteristicPoints[i])+death(lambda_n[lambda_n.size()-1]))/2 , (death(lambda_n[lambda_n.size()-1])-birth(characteristicPoints[i]))/2 ) );
                }
                lambda_n.push_back( characteristicPoints[i] );
            }
            else
            {
                newCharacteristicPoints.push_back( characteristicPoints[i] );
            }
            ++i;
        }
        lambda_n.push_back( std::make_pair(death(lambda_n[lambda_n.size()-1]),0) );
        lambda_n.push_back( std::make_pair( INT_MAX , 0 ) );

        characteristicPoints = newCharacteristicPoints;
        lambda_n.erase(std::unique(lambda_n.begin(), lambda_n.end()), lambda_n.end());
        this->land.push_back( lambda_n );
    }
}*/





double PersistenceLandscape::computeIntegralOfLandscape()const
{
    double result = 0;
    for ( size_t i = 0 ; i != this->land.size() ; ++i )
    {
        for ( size_t nr = 2 ; nr != this->land[i].size()-1 ; ++nr )
        {
            //it suffices to compute every planar integral and then sum them ap for each lambda_n
            result += 0.5*( this->land[i][nr].first - this->land[i][nr-1].first )*(this->land[i][nr].second + this->land[i][nr-1].second);
        }
    }
    return result;
}

std::pair<double,double> computeParametersOfALine( std::pair<double,double> p1 , std::pair<double,double> p2 )
{
    //p1.second = a*p1.first + b => b = p1.second - a*p1.first
    //p2.second = a*p2.first + b = a*p2.first + p1.second - a*p1.first = p1.second + a*( p2.first - p1.first )
    //=>
    //(p2.second-p1.second)/( p2.first - p1.first )  = a
    //b = p1.second - a*p1.first.
    double a = (p2.second-p1.second)/( p2.first - p1.first );
    double b = p1.second - a*p1.first;
    return std::make_pair(a,b);
}

bool computeIntegralOfLandscapeDbg = false;
double PersistenceLandscape::computeIntegralOfLandscape( double p )const
{
    double result = 0;
    for ( size_t i = 0 ; i != this->land.size() ; ++i )
    {
        for ( size_t nr = 2 ; nr != this->land[i].size()-1 ; ++nr )
        {
            if (computeIntegralOfLandscapeDbg)std::cout << "nr : " << nr << "\n";
            //In this interval, the landscape has a form f(x) = ax+b. We want to compute integral of (ax+b)^p = 1/a * (ax+b)^{p+1}/(p+1)
            std::pair<double,double> coef = computeParametersOfALine( this->land[i][nr] , this->land[i][nr-1] );
            double a = coef.first;
            double b = coef.second;

            if (computeIntegralOfLandscapeDbg)std::cout << "(" << this->land[i][nr].first << "," << this->land[i][nr].second << ") , " << this->land[i][nr-1].first << "," << this->land[i][nr].second << ")" << std::endl;
            if ( this->land[i][nr].first == this->land[i][nr-1].first )continue;
            if ( a != 0 )
            {
                result += 1/(a*(p+1)) * ( pow((a*this->land[i][nr].first+b),p+1) - pow((a*this->land[i][nr-1].first+b),p+1));
            }
            else
            {
                result += ( this->land[i][nr].first - this->land[i][nr-1].first )*( pow(this->land[i][nr].second,p) );
            }
            if ( computeIntegralOfLandscapeDbg )
            {
                std::cout << "a : " <<a << " , b : " << b << std::endl;
                std::cout << "result : " << result << std::endl;
            }
        }
        //if (computeIntegralOfLandscapeDbg) std::cin.ignore();
    }
    return result;
}

double PersistenceLandscape::computeIntegralOfLandscapeMultipliedByIndicatorFunction( std::vector<std::pair<double,double> > indicator )const
{
    PersistenceLandscape l = this->multiplyByIndicatorFunction(indicator);
    return l.computeIntegralOfLandscape();
}

double PersistenceLandscape::computeIntegralOfLandscapeMultipliedByIndicatorFunction( std::vector<std::pair<double,double> > indicator , double p )const//this function compute integral of p-th power of landscape.
{
    PersistenceLandscape l = this->multiplyByIndicatorFunction(indicator);
    return l.computeIntegralOfLandscape(p);
}


//This is a standard function which pairs maxima and minima which are not more than epsilon apart.
//This algorithm do not reduce all of them, just make one passage through data. In order to reduce all of them
//use the function reduceAllPairsOfLowPersistenceMaximaMinima( double epsilon )
//WARNING! THIS PROCEDURE MODIFIES THE LANDSCAPE!!!
unsigned PersistenceLandscape::removePairsOfLocalMaximumMinimumOfEpsPersistence(double epsilon)
{
    unsigned numberOfReducedPairs = 0;
    for ( size_t dim = 0  ; dim != this->land.size() ; ++dim )
    {
        if ( 2 > this->land[dim].size()-3 )continue; // to make sure that the loop in below is not infinite.
        for ( size_t nr = 2 ; nr != this->land[dim].size()-3 ; ++nr )
        {
            if ( (fabs(this->land[dim][nr].second - this->land[dim][nr+1].second) < epsilon) && (this->land[dim][nr].second != this->land[dim][nr+1].second) )
            {
                //right now we modify only the lalues of a points. That means that angles of lines in the landscape changes a bit. This is the easiest computational
                //way of doing this. But I am not sure if this is the best way of doing such a reduction of nonessential critical points. Think about this!
                if ( this->land[dim][nr].second < this->land[dim][nr+1].second )
                {
                    this->land[dim][nr].second = this->land[dim][nr+1].second;
                }
                else
                {
                    this->land[dim][nr+1].second = this->land[dim][nr].second;
                }
                ++numberOfReducedPairs;
            }
        }
    }
    return numberOfReducedPairs;
}

//this procedure redue all critical points of low persistence.
void PersistenceLandscape::reduceAllPairsOfLowPersistenceMaximaMinima( double epsilon )
{
    unsigned numberOfReducedPoints = 1;
    while ( numberOfReducedPoints )
    {
        numberOfReducedPoints = this->removePairsOfLocalMaximumMinimumOfEpsPersistence( epsilon );
    }
}

//It may happened that some landscape points obtained as a aresult of an algorithm lies in a line. In this case, the following procedure allows to
//remove unnecesary points.
bool reduceAlignedPointsBDG = false;
void PersistenceLandscape::reduceAlignedPoints( double tollerance )//this parapeter says how much the coeficients a and b in a formula y=ax+b may be different to consider points aligned.
{
    for ( size_t dim = 0  ; dim != this->land.size() ; ++dim )
    {
        size_t nr = 1;
        std::vector< std::pair<double,double> > lambda_n;
        lambda_n.push_back( this->land[dim][0] );
        while ( nr != this->land[dim].size()-2 )
        {
            //first, compute a and b in formula y=ax+b of a line crossing this->land[dim][nr] and this->land[dim][nr+1].
            std::pair<double,double> res = computeParametersOfALine( this->land[dim][nr] , this->land[dim][nr+1] );
            if ( reduceAlignedPointsBDG )
            {
                std::cout << "Considering points : " << this->land[dim][nr] << " and " << this->land[dim][nr+1] << std::endl;
                std::cout << "Adding : " << this->land[dim][nr] << " to lambda_n." << std::endl;
            }
            lambda_n.push_back( this->land[dim][nr] );

            double a = res.first;
            double b = res.second;
            int i = 1;
            while ( nr+i != this->land[dim].size()-2 )
            {
                if ( reduceAlignedPointsBDG )
                {
                    std::cout << "Checking if : " << this->land[dim][nr+i+1] << " is aligned with them " << std::endl;
                }
                std::pair<double,double> res1 = computeParametersOfALine( this->land[dim][nr] , this->land[dim][nr+i+1] );
                if ( (fabs(res1.first-a) < tollerance) && (fabs(res1.second-b)<tollerance) )
                {
                    if ( reduceAlignedPointsBDG ){std::cout << "It is aligned " << std::endl;}
                    ++i;
                }
                else
                {
                    if ( reduceAlignedPointsBDG ){std::cout << "It is NOT aligned " << std::endl;}
                    break;
                }
            }
            if ( reduceAlignedPointsBDG )
            {
                std::cout << "We are out of the while loop. The number of aligned points is : " << i << std::endl; //std::cin.ignore();
            }
            nr += i;
        }
        if ( reduceAlignedPointsBDG )
        {
            std::cout << "Out  of main while loop, done with this dimension " << std::endl;
            std::cout << "Adding : " << this->land[dim][ this->land[dim].size()-2 ] << " to lamnda_n " << std::endl;
            std::cout << "Adding : " << this->land[dim][ this->land[dim].size()-1 ] << " to lamnda_n " << std::endl;
            std::cin.ignore();
        }
        lambda_n.push_back( this->land[dim][ this->land[dim].size()-2 ] );
        lambda_n.push_back( this->land[dim][ this->land[dim].size()-1 ] );

        //if something was reduced, then replace this->land[dim] with the new lambda_n.
        if ( lambda_n.size() < this->land[dim].size() )
        {
            if ( lambda_n.size() > 4 )
            {
                this->land[dim].swap(lambda_n);
            }
            /*else
            {
                this->land[dim].clear();
            }*/
        }
    }
}


//Yet another function to smooth up the data. The idea of this one is as follows. Let us take a landscape point A which is not (+infty,0), (-infty,0) of (a,0), (b,0), where a and b denotes the
//points which support of the function begins and ends. Let B and C will be the landscape points after A. Suppose B and C are also no one as above.
//The question we are asking here is -- can we remove the point B and draw a line from A to C such that the difference in a landscape will be not greater than epsilon?
//To measure the penalty of removing B, the funcion penalty. In below, the simplese example is given:

double penalty(std::pair<double,double> A,std::pair<double,double> B, std::pair<double,double> C)
{
    return fabs(functionValue(A,C,B.first)-B.second);
}//penalty


bool reducePointsDBG = false;
unsigned PersistenceLandscape::reducePoints( double tollerance , double (*penalty)(std::pair<double,double> ,std::pair<double,double>,std::pair<double,double>) )
{
    unsigned numberOfPointsReduced = 0;
    for ( size_t dim = 0  ; dim != this->land.size() ; ++dim )
    {
        size_t nr = 1;
        std::vector< std::pair<double,double> > lambda_n;
        if ( reducePointsDBG )std::cout << "Adding point to lambda_n : " << this->land[dim][0] << std::endl;
        lambda_n.push_back( this->land[dim][0] );
        while ( nr <= this->land[dim].size()-2 )
        {
            if ( reducePointsDBG )std::cout << "Adding point to lambda_n : " << this->land[dim][nr] << std::endl;
            lambda_n.push_back( this->land[dim][nr] );
            if ( penalty( this->land[dim][nr],this->land[dim][nr+1],this->land[dim][nr+2] ) < tollerance )
            {
                ++nr;
                ++numberOfPointsReduced;
            }
            ++nr;
        }
        if ( reducePointsDBG )std::cout << "Adding point to lambda_n : " << this->land[dim][nr] << std::endl;
        if ( reducePointsDBG )std::cout << "Adding point to lambda_n : " <<this->land[dim][nr] << std::endl;
        lambda_n.push_back( this->land[dim][ this->land[dim].size()-2 ] );
        lambda_n.push_back( this->land[dim][ this->land[dim].size()-1 ] );

        //if something was reduced, then replace this->land[dim] with the new lambda_n.
        if ( lambda_n.size() < this->land[dim].size() )
        {
            if ( lambda_n.size() > 4 )
            {
                //CHANGE
                //this->land[dim] = lambda_n;
                this->land[dim].swap(lambda_n);
            }
            else
            {
                this->land[dim].clear();
            }
        }
    }
    return numberOfPointsReduced;
}



double findZeroOfALineSegmentBetweenThoseTwoPoints ( std::pair<double,double> p1, std::pair<double,double> p2 )
{
    if ( p1.first == p2.first )return p1.first;
    if ( p1.second*p2.second > 0 )
    {
        std::ostringstream errMessage;
        errMessage <<"In function findZeroOfALineSegmentBetweenThoseTwoPoints the agguments are: (" << p1.first << "," << p1.second << ") and (" << p2.first << "," << p2.second << "). There is no zero in line between those two points. Program terminated.";
        std::string errMessageStr = errMessage.str();
        const char* err = errMessageStr.c_str();
        throw(err);
    }
    //we assume here, that x \in [ p1.first, p2.first ] and p1 and p2 are points between which we will put the line segment
    double a = (p2.second - p1.second)/(p2.first - p1.first);
    double b = p1.second - a*p1.first;
    //cerr << "Line crossing points : (" << p1.first << "," << p1.second << ") oraz (" << p2.first << "," << p2.second << ") : \n";
    //cerr << "a : " << a << " , b : " << b << " , x : " << x << endl;
    return -b/a;
}

//this is O(log(n)) algorithm, where n is number of points in this->land.
bool computeValueAtAGivenPointDbg = false;
double PersistenceLandscape::computeValueAtAGivenPoint( unsigned level , double x )const
{
    //in such a case lambda_level = 0.
    if ( level > this->land.size() ) return 0;

    //we know that the points in this->land[level] are ordered according to x coordinate. Therefore, we can find the point by using bisection:
    unsigned coordBegin = 1;
    unsigned coordEnd = this->land[level].size()-2;

    if ( computeValueAtAGivenPointDbg )
    {
        std::cerr << "Tutaj \n";
        std::cerr << "x : " << x << "\n";
        std::cerr << "this->land[level][coordBegin].first : " << this->land[level][coordBegin].first << "\n";
        std::cerr << "this->land[level][coordEnd].first : " << this->land[level][coordEnd].first << "\n";
    }

    //in this case x is outside the support of the landscape, therefore the value of the landscape is 0.
    if ( x <= this->land[level][coordBegin].first )return 0;
    if ( x >= this->land[level][coordEnd].first )return 0;

    if (computeValueAtAGivenPointDbg)std::cerr << "Entering to the while loop \n";

    while ( coordBegin+1 != coordEnd )
    {
        if (computeValueAtAGivenPointDbg)
        {
            std::cerr << "coordBegin : " << coordBegin << "\n";
            std::cerr << "coordEnd : " << coordEnd << "\n";
            std::cerr << "this->land[level][coordBegin].first : " << this->land[level][coordBegin].first << "\n";
            std::cerr << "this->land[level][coordEnd].first : " << this->land[level][coordEnd].first << "\n";
        }


        unsigned newCord = (unsigned)floor((coordEnd+coordBegin)/2.0);

        if (computeValueAtAGivenPointDbg)
        {
            std::cerr << "newCord : " << newCord << "\n";
            std::cerr << "this->land[level][newCord].first : " << this->land[level][newCord].first << "\n";
            std::cin.ignore();
        }

        if ( this->land[level][newCord].first <= x )
        {
            coordBegin = newCord;
            if ( this->land[level][newCord].first == x )return this->land[level][newCord].second;
        }
        else
        {
            coordEnd = newCord;
        }
    }

    if (computeValueAtAGivenPointDbg)
    {
        std::cout << "x : " << x << " is between : " << this->land[level][coordBegin].first << " a  " << this->land[level][coordEnd].first << "\n";
        std::cout << "the y coords are : " << this->land[level][coordBegin].second << " a  " << this->land[level][coordEnd].second << "\n";
        std::cerr << "coordBegin : " << coordBegin << "\n";
        std::cerr << "coordEnd : " << coordEnd << "\n";
        std::cin.ignore();
    }
    return functionValue( this->land[level][coordBegin] , this->land[level][coordEnd] , x );
}

std::ostream& operator<<(std::ostream& out, PersistenceLandscape& land )
{
    for ( size_t level = 0 ; level != land.land.size() ; ++level )
    {
        out << "Lambda_" << level << ":" << std::endl;
        for ( size_t i = 0 ; i != land.land[level].size() ; ++i )
        {
            if ( land.land[level][i].first == INT_MIN )
            {
                out << "-inf";
            }
            else
            {
                if ( land.land[level][i].first == INT_MAX )
                {
                    out << "+inf";
                }
                else
                {
                    out << land.land[level][i].first;
                }
            }
            out << " , " << land.land[level][i].second << std::endl;
        }
    }
    return out;
}




void PersistenceLandscape::multiplyLanscapeByRealNumberOverwrite( double x )
{
    for ( size_t dim = 0 ; dim != this->land.size() ; ++dim )
    {
        for ( size_t i = 0 ; i != this->land[dim].size() ; ++i )
        {
             this->land[dim][i].second *= x;
        }
    }
}

bool AbsDbg = false;
PersistenceLandscape PersistenceLandscape::abs()
{
    PersistenceLandscape result;
    for ( size_t level = 0 ; level != this->land.size() ; ++level )
    {
        if ( AbsDbg ){ std::cout << "level: " << level << std::endl; }
        std::vector< std::pair<double,double> > lambda_n;
        lambda_n.push_back( std::make_pair( INT_MIN , 0 ) );
        for ( size_t i = 1 ; i != this->land[level].size() ; ++i )
        {
            if ( AbsDbg ){std::cout << "this->land[" << level << "][" << i << "] : " << this->land[level][i] << std::endl;}
            //if a line segment between this->land[level][i-1] and this->land[level][i] crosses the x-axis, then we have to add one landscape point t oresult
            if ( (this->land[level][i-1].second)*(this->land[level][i].second)  < 0 )
            {
                double zero = findZeroOfALineSegmentBetweenThoseTwoPoints( this->land[level][i-1] , this->land[level][i] );

                lambda_n.push_back( std::make_pair(zero , 0) );
                lambda_n.push_back( std::make_pair(this->land[level][i].first , fabs(this->land[level][i].second)) );
                if ( AbsDbg )
                {
                    std::cout << "Adding pair : (" << zero << ",0)" << std::endl;
                    std::cout << "In the same step adding pair : (" << this->land[level][i].first << "," << fabs(this->land[level][i].second) << ") " << std::endl;
                    std::cin.ignore();
                }
            }
            else
            {
                lambda_n.push_back( std::make_pair(this->land[level][i].first , fabs(this->land[level][i].second)) );
                if ( AbsDbg )
                {
                    std::cout << "Adding pair : (" << this->land[level][i].first << "," << fabs(this->land[level][i].second) << ") " << std::endl;
                    std::cin.ignore();
                }
            }
        }
        result.land.push_back( lambda_n );
    }
    return result;
}


PersistenceLandscape PersistenceLandscape::multiplyLanscapeByRealNumberNotOverwrite( double x )const
{
    std::vector< std::vector< std::pair<double,double> > > result(this->land.size());
    for ( size_t dim = 0 ; dim != this->land.size() ; ++dim )
    {
        std::vector< std::pair<double,double> > lambda_dim( this->land[dim].size() );
        for ( size_t i = 0 ; i != this->land[dim].size() ; ++i )
        {
            lambda_dim[i] = std::make_pair( this->land[dim][i].first , x*this->land[dim][i].second );
        }
        result[dim] = lambda_dim;
    }
    PersistenceLandscape res;
    res.dimension = this->dimension;
    //CHANGE
    //res.land = result;
    res.land.swap(result);
    return res;
}//multiplyLanscapeByRealNumberOverwrite


bool operationOnPairOfLandscapesDBG = false;
PersistenceLandscape operationOnPairOfLandscapes ( const PersistenceLandscape& land1 ,  const PersistenceLandscape& land2 , double (*oper)(double,double) )
{
    if ( operationOnPairOfLandscapesDBG ){std::cout << "operationOnPairOfLandscapes\n";std::cin.ignore();}
    PersistenceLandscape result;
    std::vector< std::vector< std::pair<double,double> > > land( std::max( land1.land.size() , land2.land.size() ) );
    result.land = land;

    for ( size_t i = 0 ; i != std::min( land1.land.size() , land2.land.size() ) ; ++i )
    {
        std::vector< std::pair<double,double> > lambda_n;
        int p = 0;
        int q = 0;
        while ( (p+1 < land1.land[i].size()) && (q+1 < land2.land[i].size()) )
        {
            if ( operationOnPairOfLandscapesDBG )
            {
                std::cerr << "p : " << p << "\n";
                std::cerr << "q : " << q << "\n";
                std::cout << "land1.land[i][p].first : " << land1.land[i][p].first << "\n";
                std::cout << "land2.land[i][q].first : " << land2.land[i][q].first << "\n";
            }

            if ( land1.land[i][p].first < land2.land[i][q].first )
            {
                if ( operationOnPairOfLandscapesDBG )
                {
                    std::cout << "first \n";
                    std::cout << " functionValue(land2.land[i][q-1],land2.land[i][q],land1.land[i][p].first) : "<<  functionValue(land2.land[i][q-1],land2.land[i][q],land1.land[i][p].first) << "\n";
                    std::cout << "oper( " << land1.land[i][p].second <<"," << functionValue(land2.land[i][q-1],land2.land[i][q],land1.land[i][p].first) << " : " << oper( land1.land[i][p].second , functionValue(land2.land[i][q-1],land2.land[i][q],land1.land[i][p].first) ) << "\n";
                }
                lambda_n.push_back( std::make_pair( land1.land[i][p].first , oper( land1.land[i][p].second , functionValue(land2.land[i][q-1],land2.land[i][q],land1.land[i][p].first) ) ) );
                ++p;
                continue;
            }
            if ( land1.land[i][p].first > land2.land[i][q].first )
            {
                if ( operationOnPairOfLandscapesDBG )
                {
                    std::cout << "Second \n";
                    std::cout << "functionValue("<< land1.land[i][p-1]<<" ,"<< land1.land[i][p]<<", " << land2.land[i][q].first<<" ) : " << functionValue( land1.land[i][p-1] , land1.land[i][p-1] ,land2.land[i][q].first ) << "\n";
                    std::cout << "oper( " << functionValue( land1.land[i][p] , land1.land[i][p-1] ,land2.land[i][q].first ) <<"," << land2.land[i][q].second <<" : " << oper( land2.land[i][q].second , functionValue( land1.land[i][p] , land1.land[i][p-1] ,land2.land[i][q].first ) ) << "\n";
                }
                lambda_n.push_back( std::make_pair( land2.land[i][q].first , oper( functionValue( land1.land[i][p] , land1.land[i][p-1] ,land2.land[i][q].first ) , land2.land[i][q].second )  )  );
                ++q;
                continue;
            }
            if ( land1.land[i][p].first == land2.land[i][q].first )
            {
                if (operationOnPairOfLandscapesDBG)std::cout << "Third \n";
                lambda_n.push_back( std::make_pair( land2.land[i][q].first , oper( land1.land[i][p].second , land2.land[i][q].second ) ) );
                ++p;++q;
            }
            if (operationOnPairOfLandscapesDBG){std::cout << "Next iteration \n";getchar();}
        }
        while ( (p+1 < land1.land[i].size())&&(q+1 >= land2.land[i].size()) )
        {
            if (operationOnPairOfLandscapesDBG)
            {
                std::cout << "New point : " << land1.land[i][p].first << "  oper(land1.land[i][p].second,0) : " <<  oper(land1.land[i][p].second,0) << std::endl;
            }
            lambda_n.push_back( std::make_pair(land1.land[i][p].first , oper(land1.land[i][p].second,0) ) );
            ++p;
        }
        while ( (p+1 >= land1.land[i].size())&&(q+1 < land2.land[i].size()) )
        {
            if (operationOnPairOfLandscapesDBG)
            {
                std::cout << "New point : " << land2.land[i][q].first << " oper(0,land2.land[i][q].second) : " <<  oper(0,land2.land[i][q].second) << std::endl;
            }
            lambda_n.push_back( std::make_pair(land2.land[i][q].first , oper(0,land2.land[i][q].second) ) );
            ++q;
        }
        lambda_n.push_back( std::make_pair( INT_MAX , 0 ) );
        //CHANGE
        //result.land[i] = lambda_n;
        result.land[i].swap(lambda_n);
    }
    if ( land1.land.size() > std::min( land1.land.size() , land2.land.size() ) )
    {
        if (operationOnPairOfLandscapesDBG){std::cout << "land1.land.size() > std::min( land1.land.size() , land2.land.size() )" << std::endl;}
        for ( size_t i = std::min( land1.land.size() , land2.land.size() ) ; i != std::max( land1.land.size() , land2.land.size() ) ; ++i )
        {
            std::vector< std::pair<double,double> > lambda_n( land1.land[i] );
            for ( size_t nr = 0 ; nr != land1.land[i].size() ; ++nr )
            {
                lambda_n[nr] = std::make_pair( land1.land[i][nr].first , oper( land1.land[i][nr].second , 0 ) );
            }
            //CHANGE
            //result.land[i] = lambda_n;
            result.land[i].swap(lambda_n);
        }
    }
    if ( land2.land.size() > std::min( land1.land.size() , land2.land.size() ) )
    {
        if (operationOnPairOfLandscapesDBG){std::cout << "( land2.land.size() > std::min( land1.land.size() , land2.land.size() ) ) " << std::endl;}
        for ( size_t i = std::min( land1.land.size() , land2.land.size() ) ; i != std::max( land1.land.size() , land2.land.size() ) ; ++i )
        {
            std::vector< std::pair<double,double> > lambda_n( land2.land[i] );
            for ( size_t nr = 0 ; nr != land2.land[i].size() ; ++nr )
            {
                lambda_n[nr] = std::make_pair( land2.land[i][nr].first , oper( 0 , land2.land[i][nr].second ) );
            }
            //CHANGE
            //result.land[i] = lambda_n;
            result.land[i].swap(lambda_n);
        }
    }
    if ( operationOnPairOfLandscapesDBG ){std::cout << "operationOnPairOfLandscapes\n";std::cin.ignore();}
    return result;
}//operationOnPairOfLandscapes



double computeMaximalDistanceNonSymmetric( const PersistenceLandscape& pl1, const PersistenceLandscape& pl2 , unsigned& nrOfLand , double&x , double& y1, double& y2 )
{
    //this distance is not symmetric. It compute ONLY distance between inflection points of pl1 and pl2.
    double maxDist = 0;
    int minimalNumberOfLevels = std::min( pl1.land.size() , pl2.land.size() );
    for ( int level = 0 ; level != minimalNumberOfLevels ; ++level )
    {
        int p2Count = 0;
        for ( int i = 1 ; i != pl1.land[level].size()-1 ; ++i ) //w tym przypadku nie rozwarzam punktow w nieskocznosci
        {
            while ( true )
            {
                if (  (pl1.land[level][i].first>=pl2.land[level][p2Count].first) && (pl1.land[level][i].first<=pl2.land[level][p2Count+1].first)  )break;
                p2Count++;
            }
            double val = fabs( functionValue( pl2.land[level][p2Count] , pl2.land[level][p2Count+1] , pl1.land[level][i].first ) - pl1.land[level][i].second);

            //std::cerr << "functionValue( pl2.land[level][p2Count] , pl2.land[level][p2Count+1] , pl1.land[level][i].first ) : " << functionValue( pl2.land[level][p2Count] , pl2.land[level][p2Count+1] , pl1.land[level][i].first ) << "\n";
            //std::cerr << "pl1.land[level][i].second : " << pl1.land[level][i].second << "\n";
            //std::cerr << "pl1.land[level][i].first :" << pl1.land[level][i].first << "\n";
            //std::cin.ignore();

            if ( maxDist <= val )
            {
                maxDist = val;
                nrOfLand = level;
                x = pl1.land[level][i].first;
                y1 = pl1.land[level][i].second;
                y2 = functionValue( pl2.land[level][p2Count] , pl2.land[level][p2Count+1] , pl1.land[level][i].first );
            }
       }
    }

    if ( minimalNumberOfLevels < pl1.land.size() )
    {
        for ( int level = minimalNumberOfLevels ; level != pl1.land.size() ; ++ level )
        {
            for ( int i = 0 ; i != pl1.land[level].size() ; ++i )
            {
                if ( maxDist < pl1.land[level][i].second )
                {
                    maxDist = pl1.land[level][i].second;
                    nrOfLand = level;
                    x = pl1.land[level][i].first;
                    y1 = pl1.land[level][i].second;
                    y2 = 0;
                }
            }
        }
    }
    return maxDist;
}

double computeMaxNormDiscanceOfLandscapes( const PersistenceLandscape& first, const PersistenceLandscape& second , unsigned& nrOfLand , double&x , double& y1, double& y2 )
{
    unsigned nrOfLandFirst;
    double xFirst, y1First, y2First;
    double dFirst = computeMaximalDistanceNonSymmetric(first,second,nrOfLandFirst,xFirst, y1First, y2First);

    unsigned nrOfLandSecond;
    double xSecond, y1Second, y2Second;
    double dSecond = computeMaximalDistanceNonSymmetric(second,first,nrOfLandSecond,xSecond, y1Second, y2Second);

    if ( dFirst > dSecond )
    {
        nrOfLand = nrOfLandFirst;
        x = xFirst;
        y1 = y1First;
        y2 = y2First;
    }
    else
    {
        nrOfLand = nrOfLandSecond;
        x = xSecond;
        //this twist in below is neccesary!
        y2 = y1Second;
        y1 = y2Second;
        //y1 = y1Second;
        //y2 = y2Second;
    }
    return std::max( dFirst , dSecond );
}


double computeMaximalDistanceNonSymmetric( const PersistenceLandscape& pl1, const PersistenceLandscape& pl2 )
{
    bool dbg = false;
    if (dbg)std::cerr << " computeMaximalDistanceNonSymmetric \n";
    //this distance is not symmetric. It compute ONLY distance between inflection points of pl1 and pl2.
    double maxDist = 0;
    int minimalNumberOfLevels = std::min( pl1.land.size() , pl2.land.size() );
    for ( int level = 0 ; level != minimalNumberOfLevels ; ++ level )
    {
        if (dbg)
        {
            std::cerr << "Level : " << level << std::endl;
            std::cerr << "PL1 : \n";
            for ( int i = 0 ; i  != pl1.land[level].size() ; ++i )
            {
                std::cerr << "(" <<pl1.land[level][i].first << "," << pl1.land[level][i].second << ") \n";
            }
            std::cerr << "PL2 : \n";
            for ( int i = 0 ; i  != pl2.land[level].size() ; ++i )
            {
                std::cerr << "(" <<pl2.land[level][i].first << "," << pl2.land[level][i].second << ") \n";
            }
            std::cin.ignore();
        }

        int p2Count = 0;
        for ( int i = 1 ; i != pl1.land[level].size()-1 ; ++i ) //w tym przypadku nie rozwarzam punktow w nieskocznosci
        {
            while ( true )
            {
                if (  (pl1.land[level][i].first>=pl2.land[level][p2Count].first) && (pl1.land[level][i].first<=pl2.land[level][p2Count+1].first)  )break;
                p2Count++;
            }
            double val = fabs( functionValue( pl2.land[level][p2Count] , pl2.land[level][p2Count+1] , pl1.land[level][i].first ) - pl1.land[level][i].second);
            if ( maxDist <= val )maxDist = val;

            if (dbg)
            {
                std::cerr << pl1.land[level][i].first <<"in [" << pl2.land[level][p2Count].first << "," <<  pl2.land[level][p2Count+1].first <<"] \n";
                std::cerr << "pl1[level][i].second : " << pl1.land[level][i].second << std::endl;
                std::cerr << "functionValue( pl2[level][p2Count] , pl2[level][p2Count+1] , pl1[level][i].first ) : " << functionValue( pl2.land[level][p2Count] , pl2.land[level][p2Count+1] , pl1.land[level][i].first ) << std::endl;
                std::cerr << "val : "  << val << std::endl;
                std::cin.ignore();
            }
        }
    }

    if (dbg)std::cerr << "minimalNumberOfLevels : " << minimalNumberOfLevels << std::endl;

    if ( minimalNumberOfLevels < pl1.land.size() )
    {
        for ( int level = minimalNumberOfLevels ; level != pl1.land.size() ; ++ level )
        {
            for ( int i = 0 ; i != pl1.land[level].size() ; ++i )
            {
                if (dbg)std::cerr << "pl1[level][i].second  : " << pl1.land[level][i].second << std::endl;
                if ( maxDist < pl1.land[level][i].second )maxDist = pl1.land[level][i].second;
            }
        }
    }
    return maxDist;
}




double computeDiscanceOfLandscapes( const PersistenceLandscape& first, const PersistenceLandscape& second , unsigned p )
{
    //This is what we want to compute: (\int_{- \infty}^{+\infty}| first-second |^p)^(1/p). We will do it one step at a time:

    //first-second :
    PersistenceLandscape lan = first-second;

    //| first-second |:
    lan = lan.abs();

    //\int_{- \infty}^{+\infty}| first-second |^p
    double result;
    if ( p != 1 )
    {
        result = lan.computeIntegralOfLandscape(p);
    }
    else
    {
        result = lan.computeIntegralOfLandscape();
    }

    //(\int_{- \infty}^{+\infty}| first-second |^p)^(1/p)
    return pow( result , 1/(double)p );
}

double computeMaxNormDiscanceOfLandscapes( const PersistenceLandscape& first, const PersistenceLandscape& second )
{
    return std::max( computeMaximalDistanceNonSymmetric(first,second) , computeMaximalDistanceNonSymmetric(second,first) );
}


bool comparePairsForMerging( std::pair< double , unsigned > first , std::pair< double , unsigned > second )
{
    return (first.first < second.first);
}


std::vector< std::pair< double , unsigned > > PersistenceLandscape::generateBettiNumbersHistogram()const
{
    bool dbg = false;

    std::vector< std::pair< double , unsigned > > resultRaw;

    for ( size_t dim = 0 ; dim != this->land.size() ; ++dim )
    {
        std::vector< std::pair< double , unsigned > > rangeOfLandscapeInThisDimension;
        if ( dim > 0 )
        {
            for ( size_t i = 1 ; i != this->land[dim].size()-1 ; ++i )
            {
                if ( this->land[dim][i].second == 0 )
                {
                    rangeOfLandscapeInThisDimension.push_back(std::make_pair(this->land[dim][i].first , dim+1));
                }
            }
        }
        else
        {
            //dim == 0.
            bool first = true;
            for ( size_t i = 1 ; i != this->land[dim].size()-1 ; ++i )
            {
                if ( this->land[dim][i].second == 0 )
                {
                    if ( first ){ rangeOfLandscapeInThisDimension.push_back(std::make_pair(this->land[dim][i].first , 0)); }
                    rangeOfLandscapeInThisDimension.push_back(std::make_pair(this->land[dim][i].first , dim+1));
                    if ( !first ){ rangeOfLandscapeInThisDimension.push_back(std::make_pair(this->land[dim][i].first , 0)); }
                    first = !first;
                }
            }
        }
        std::vector< std::pair< double , unsigned > > resultRawNew( resultRaw.size() + rangeOfLandscapeInThisDimension.size() );
        std::merge( resultRaw.begin() , resultRaw.end() , rangeOfLandscapeInThisDimension.begin() , rangeOfLandscapeInThisDimension.end() , resultRawNew.begin() , comparePairsForMerging );
        resultRaw.swap( resultRawNew );
        if ( dbg )
        {
            std::cerr << "Raw result : for dim : " << dim << std::endl;
            for ( size_t i = 0 ;  i != resultRaw.size() ; ++i )
            {
                std::cerr << "(" << resultRaw[i].first << " , " << resultRaw[i].second << ")" << std::endl;
            }
            getchar();
        }

    }

    if ( dbg )
    {
        std::cerr << "Raw result : " << std::endl;
        for ( size_t i = 0 ;  i != resultRaw.size() ; ++i )
        {
            std::cerr << "(" << resultRaw[i].first << " , " << resultRaw[i].second << ")" << std::endl;
        }
        getchar();
    }

    //now we should make it into a step function by adding a points in the jumps:
    std::vector< std::pair< double , unsigned > > result;
    if ( resultRaw.size() == 0 )return result;
    for ( size_t i = 1 ;  i != resultRaw.size() ; ++i )
    {
        result.push_back( resultRaw[i-1] );
        if ( resultRaw[i-1].second <= resultRaw[i].second )
        {
            result.push_back( std::make_pair( resultRaw[i].first , resultRaw[i-1].second ) );
        }
        else
        {
            result.push_back( std::make_pair( resultRaw[i-1].first , resultRaw[i].second ) );
        }
    }
    result.erase( unique( result.begin(), result.end() ), result.end() );

/*
    //cleaning for Cathy
    std::vector< std::pair< double , unsigned > > resultNew;
    size_t i = 0;
    while ( i != result.size() )
    {
        int j = 1;
        resultNew.push_back( std::make_pair(result[i].first , maxBetti) );
        unsigned maxBetti = result[i].second;
        while ( (i+j<=result.size() ) && (result[i].first == result[i+j].first) )
        {
            if ( maxBetti < result[i+j].second ){maxBetti = result[i+j].second;}
            ++j;
        }
        //i += std::max(j,1);
        resultNew.push_back( std::make_pair(result[i].first , maxBetti) );
        i += j;
    }
    result.swap(resultNew);
*/
    std::vector< std::pair< double , unsigned > > resultNew;
    size_t i = 0 ;
    while ( i != result.size() )
    {
        double x = result[i].first;
        double maxBetti = result[i].second;
        double minBetti = result[i].second;
        while ( (i != result.size()) && (fabs(result[i].first - x) < 0.000001) )
        {
            if ( maxBetti < result[i].second )maxBetti = result[i].second;
            if ( minBetti > result[i].second )minBetti = result[i].second;
            ++i;
        }
        if ( minBetti != maxBetti )
        {
            if ( (resultNew.size() == 0) || (resultNew[resultNew.size()-1].second <= minBetti) )
            {
                //going up
                resultNew.push_back( std::make_pair( x , minBetti ) );
                resultNew.push_back( std::make_pair( x , maxBetti ) );
            }
            else
            {
                //going down
                resultNew.push_back( std::make_pair( x , maxBetti ) );
                resultNew.push_back( std::make_pair( x , minBetti ) );
            }
        }
        else
        {
            resultNew.push_back( std::make_pair( x , minBetti ) );
        }
    }
    result.swap(resultNew);

    if ( dbg )
    {
        std::cerr << "Final result : " << std::endl;
        for ( size_t i = 0 ;  i != result.size() ; ++i )
        {
            std::cerr << "(" << result[i].first << " , " << result[i].second << ")" << std::endl;
        }
        getchar();
    }
    return result;
}//generateBettiNumbersHistogram


void PersistenceLandscape::printBettiNumbersHistoramIntoFileAndGenerateGnuplotCommand( char* filename )const
{
    std::vector< std::pair< double , unsigned > > histogram = this->generateBettiNumbersHistogram();
    std::ostringstream result;
    for ( size_t i = 0 ; i != histogram.size() ; ++i )
    {
        result << histogram[i].first << " " << histogram[i].second << std::endl;
    }
    std::ofstream write;
    write.open( filename );
    write << result.str();
    write.close();
    std::cout << "The result is in the file : " << filename <<" . Now in gnuplot type plot \"" << filename << "\" with lines" << std::endl;
}//printBettiNumbersHistoramIntoFileAndGenerateGnuplotCommand



#endif
