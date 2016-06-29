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


#ifndef PERISTENCEBARCODES_H
#define PERISTENCEBARCODES_H

#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
#include <algorithm>
#include <cmath>
#include <climits>
#include <map>
#include <climits>
#include <fstream>

//#include "configure.h"
//global variables and their default values.
bool areThereInfiniteIntervals = false;
double infty = -1;
bool shallInfiniteBarcodesBeIgnored = true;
double valueOfInfinity = INT_MAX;
bool useGridInComputations = false;
double gridDiameter = 0.01;
double epsi = 0.000005;

//code taken from http://ranger.uta.edu/~weems/NOTES5311/hungarian.c
#include "hungarianC.h"









double computeDistanceOfPointsInPlane( std::pair<double,double> p1 , std::pair<double,double> p2 )
{
    //std::cerr << "Computing distance of points : (" << p1.first << "," << p1.second << ") and (" << p2.first << "," << p2.second << ")\n";
    //std::cerr << "Distance : " << sqrt( (p1.first-p2.first)*(p1.first-p2.first) + (p1.second-p2.second)*(p1.second-p2.second) ) << "\n";
    return sqrt( (p1.first-p2.first)*(p1.first-p2.first) + (p1.second-p2.second)*(p1.second-p2.second) );
}//computeDistanceOfPointsInPlane


std::pair<double,double> projectionToDiagonal( std::pair<double,double> p )
{
    return std::make_pair( 0.5*(p.first+p.second),0.5*(p.first+p.second) );
}



//to write individual bar
std::ostream& operator<<(std::ostream& out, std::pair<double,double> p )
{
    out << p.first << " " << p.second;
    return out;
}


//this class represent a barcodes in a given dimension.
class PersistenceBarcodes
{
public:
    PersistenceBarcodes(){};
    PersistenceBarcodes(const PersistenceBarcodes& orgyginal);
    PersistenceBarcodes(const char* filename);
    PersistenceBarcodes(const char* filename , double begin , double step);
    PersistenceBarcodes( std::vector< std::pair<double,double> > );
    PersistenceBarcodes(const char* filename , unsigned dimensionOfBarcode);
    PersistenceBarcodes( std::vector< std::pair<double,double> > , unsigned dimensionOfBarcode);
    PersistenceBarcodes operator = ( const PersistenceBarcodes& rhs );

    void writeToFile( char* filename );

    void putToAFileHistogramOfBarcodesLengths( char* filename , size_t howMany , bool shouldWePutAlsoResponsibleBarcodes );
    void putToAFileHistogramOfBarcodesLengths( char* filename , size_t beginn , size_t endd , bool shouldWePutAlsoResponsibleBarcodes );

    void removeShortBarcodes( double minimalDiameterOfBarcode );

    void addPair( double b , double d ){this->barcodes.push_back( std::make_pair(b,d) );}

    double computeLandscapeIntegralFromBarcodes();

    void putToBins( size_t numberOfBins );

    friend std::pair< double , std::vector< std::pair< std::pair<double,double>,std::pair<double,double> > > > computeBottleneckDistance( const PersistenceBarcodes& first, const PersistenceBarcodes& second , unsigned p );

    friend std::ostream& operator<<(std::ostream& out, PersistenceBarcodes& bar )
    {
        for ( size_t i = 0 ; i != bar.barcodes.size() ; ++i )
        {
            out << bar.barcodes[i].first << " " << bar.barcodes[i].second << std::endl;
        }
        return out;
    }
    size_t size()const{return this->barcodes.size();}
    bool empty()const{return (this->barcodes.size() == 0);}
    unsigned dim()const{return this->dimensionOfBarcode;}

    //iterators
    typedef std::vector< std::pair<double,double> >::iterator bIterator;
    bIterator bBegin(){return this->barcodes.begin();}
    bIterator bEnd(){return this->barcodes.end();}

    friend class PersistenceLandscape;


    std::pair<double,double> minMax()const;

    PersistenceBarcodes restrictBarcodesToGivenInterval( std::pair<double,double> interval );

    double computeAverageOfMidpointOfBarcodes();
    double computeAverageOfMidpointOfBarcodesWeightedByLength();

    //this  procedure shift all the barcodes so that the averaged center of barcode is 0 and the averaged length of a barcode is 1.
    void setAverageMidpointToZero();
    void setAveragedLengthToOne();
    void averageBarcodes();

    void setRangeToMinusOneOne();
    void setRange( double beginn , double endd );


    void sort();
    bool compare( PersistenceBarcodes& b );

    void writeBarcodesSortedAccordingToLengthToAFile( char* filename );

    void removeBarcodesThatBeginsBeforeGivenNumber( double number );

    void plot( char* filename );

//TODO uncomment
private:
    std::vector< std::pair<double,double> > barcodes;
    unsigned dimensionOfBarcode;
};

void PersistenceBarcodes::plot( char* filename )
{
    //this program create a gnuplot script file that allows to plot persistence diagram.
    std::ofstream out;

    std::ostringstream nameSS;
    nameSS << filename << "_GnuplotScript";
    std::string nameStr = nameSS.str();

    out.open( (char*)nameStr.c_str() );
    std::pair<double,double> minMaxValues = this->minMax();
    out << "set xrange [" << minMaxValues.first - 0.1*(minMaxValues.second-minMaxValues.first) << " : " << minMaxValues.second + 0.1*(minMaxValues.second-minMaxValues.first) << " ]" << std::endl;
    out << "set yrange [" << minMaxValues.first - 0.1*(minMaxValues.second-minMaxValues.first) << " : " << minMaxValues.second + 0.1*(minMaxValues.second-minMaxValues.first) << " ]" << std::endl;

    //out << "set xrange [0:40]" << std::endl;
    //out << "set yrange [0:40]" << std::endl;

    out << "plot '-' using 1:2 title \"" << filename << "\", \\" << std::endl;
    out << "     '-' using 1:2 notitle with lp" << std::endl;
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        out << this->barcodes[i].first << " " << this->barcodes[i].second << std::endl;
    }
    out << "EOF" << std::endl;
    out << minMaxValues.first - 0.1*(minMaxValues.second-minMaxValues.first) << " " << minMaxValues.first - 0.1*(minMaxValues.second-minMaxValues.first) << std::endl;
    out << minMaxValues.second + 0.1*(minMaxValues.second-minMaxValues.first) << " " << minMaxValues.second + 0.1*(minMaxValues.second-minMaxValues.first) << std::endl;
    //out << "0 0" << std::endl << "40 40" << std::endl;
    out.close();

    std::cout << "Gnuplot script to visualize persistence diagram written to the file: " << nameStr << ". Type load '" << nameStr << "' in gnuplot to visualize." << std::endl;
}

bool compareAccordingToLength( const std::pair<double,double>& f , const std::pair<double,double>& s )
{
    double l1 = fabs(f.second - f.first);
    double l2 = fabs(s.second - s.first);
    return (l1 > l2);
}

void PersistenceBarcodes::removeBarcodesThatBeginsBeforeGivenNumber( double number )
{
    std::vector< std::pair<double,double> > newBarcodes;
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        if ( this->barcodes[i].first > number )
        {
            newBarcodes.push_back( this->barcodes[i] );
        }
        else
        {
            //this->barcodes[i].first <= number
            if ( this->barcodes[i].second > number )
            {
                newBarcodes.push_back( std::make_pair( number , this->barcodes[i].second) );
            }
            //in the opposite case this->barcodes[i].second <= in which case, we totally ignore this point.
        }
    }
    this->barcodes.swap(newBarcodes);
}

void PersistenceBarcodes::writeBarcodesSortedAccordingToLengthToAFile( char* filename )
{
    //first sort the bars according to their length
    std::vector< std::pair<double,double> > sortedBars;
    sortedBars.insert( sortedBars.end() , this->barcodes.begin() , this->barcodes.end() );
    std::sort( sortedBars.begin() , sortedBars.end() ,compareAccordingToLength );

    std::ofstream out;
    out.open(filename);
    for ( size_t i = 0 ; i != sortedBars.size() ; ++i )
    {
        out << sortedBars[i].first << " " << sortedBars[i].second << std::endl;
    }
    out.close();
}

void PersistenceBarcodes::putToBins( size_t numberOfBins )
{
    bool dbg = false;
    std::pair<double,double> minMax = this->minMax();
    std::vector< std::pair< double , double > > binnedData;
    double dx = ( minMax.second - minMax.first )/(double)numberOfBins;

    if ( dbg )
    {
        std::cerr << "Min : " << minMax.first << std::endl;
        std::cerr << "Max : " << minMax.second << std::endl;
        std::cerr << "dx : " << dx << std::endl;
    }

    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        size_t leftBinNumber = floor( (this->barcodes[i].first - minMax.first)/dx );
        size_t rightBinNumber = floor( (this->barcodes[i].second - minMax.first)/dx );

        double leftBinEnd = (leftBinNumber+0.5)*dx;
        double rightBinEnd = (rightBinNumber+0.5)*dx;

        if ( leftBinEnd != rightBinEnd ){binnedData.push_back( std::make_pair(leftBinEnd , rightBinEnd) );}
    }
    this->barcodes.swap(binnedData);
}


bool comparePairs( const std::pair<double,double>& f , const std::pair<double,double>& s )
{
    if ( f.first < s.first )return true;
    if ( f.first > s.first )return false;
    if ( f.second < s.second )return true;
    return false;
}
void PersistenceBarcodes::sort()
{
    std::sort( this->barcodes.begin() , this->barcodes.end() , comparePairs );
}//sort
bool PersistenceBarcodes::compare( PersistenceBarcodes& b )
{
    bool dbg = true;
    if ( dbg )
    {
        std::cerr << "this->barcodes.size() : " << this->barcodes.size() << std::endl;
        std::cerr << "b.barcodes.size() : " << b.barcodes.size() << std::endl;
    }
    if ( this->barcodes.size() != b.barcodes.size() )return false;
    this->sort();
    b.sort();
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        if ( this->barcodes[i] != b.barcodes[i] )
        {
            std::cerr << "this->barcodes["<<i<<"] = " << this->barcodes[i] << std::endl;
            std::cerr << "b.barcodes["<<i<<"] = " << b.barcodes[i] << std::endl;
            getchar();
            return false;
        }
    }
    return true;
}

size_t minn( size_t f, size_t s )
{
    if ( f < s )return f;
    return s;
}


double PersistenceBarcodes::computeAverageOfMidpointOfBarcodes()
{
    double averages = 0;
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        averages += 0.5*(this->barcodes[i].second - this->barcodes[i].first);
    }
    averages /= this->barcodes.size();

    return averages;
}//computeAverageOfMidpointOfBarcodes


void PersistenceBarcodes::setAverageMidpointToZero()
{
    bool dbg = false;
    //double average = this->computeAverageOfMidpointOfBarcodes();
    double average = computeAverageOfMidpointOfBarcodesWeightedByLength();

    if (dbg){std::cerr << "average : " << average << std::endl;}

    //shift every barcode by -average
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        this->barcodes[i].first -= average;
        this->barcodes[i].second -= average;
    }
}

void PersistenceBarcodes::setAveragedLengthToOne()
{
    //first compute average length of barcode:
    size_t sumOfLengths = 0;
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        sumOfLengths += fabs( this->barcodes[i].second - this->barcodes[i].first );
    }
    double averageLength = (double)sumOfLengths / (double)this->barcodes.size();
    //now we need to rescale the length by 1/averageLength

    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        double midpoint = 0.5 * (this->barcodes[i].first+this->barcodes[i].second);
        double length = fabs( this->barcodes[i].first-this->barcodes[i].second )/averageLength;
        this->barcodes[i].first = midpoint - length/2;
        this->barcodes[i].second = midpoint + length/2;
    }
}

void PersistenceBarcodes::averageBarcodes()
{
    this->setAverageMidpointToZero();
    this->setAveragedLengthToOne();
}


void PersistenceBarcodes::setRangeToMinusOneOne()
{
    //first we need to find min and max endpoint of intervals:
    double minn = INT_MAX;
    double maxx = -INT_MAX;
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        double a = this->barcodes[i].first;
        double b = this->barcodes[i].second;
        if ( b < a )std::swap(a,b);

        if ( a < minn )minn = a;
        if ( b > maxx )maxx = b;
    }

    double shiftValue = -minn;
    maxx += shiftValue;
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        this->barcodes[i].first += shiftValue;
        this->barcodes[i].first /= maxx;
        this->barcodes[i].second += shiftValue;
        this->barcodes[i].second /= maxx;
    }
}

void PersistenceBarcodes::setRange( double beginn , double endd )
{
    if ( beginn >= endd )throw("Bar ranges in the setRange procedure.");
    std::pair< double , double > minMax = this->minMax();

    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        double originalBegin = this->barcodes[i].first;
        double originalEnd = this->barcodes[i].second;

        double newBegin = beginn + ( originalBegin - minMax.first )*(endd-beginn)/( minMax.second - minMax.first );
        double newEnd = beginn + ( originalEnd - minMax.first )*(endd-beginn)/( minMax.second - minMax.first );

        this->barcodes[i].first = newBegin;
        this->barcodes[i].second = newEnd;
    }
}

void PersistenceBarcodes::writeToFile( char* filename )
{
    std::ofstream out;
    out.open( filename );
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        out << this->barcodes[i].first << " " << this->barcodes[i].second << std::endl;
    }
    out.close();
}

double PersistenceBarcodes::computeAverageOfMidpointOfBarcodesWeightedByLength()
{
    double averageBarcodeLength = 0;
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        averageBarcodeLength += (this->barcodes[i].second - this->barcodes[i].first);
    }
    averageBarcodeLength /= this->barcodes.size();

    double weightedAverageOfBarcodesMidpoints = 0;
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        double weight = (this->barcodes[i].second - this->barcodes[i].first)/averageBarcodeLength;
        weightedAverageOfBarcodesMidpoints += weight * 0.5*(this->barcodes[i].second - this->barcodes[i].first);
    }
    weightedAverageOfBarcodesMidpoints /= this->barcodes.size();

    //YTANIE< CZY TO MA SENS???


    return weightedAverageOfBarcodesMidpoints;
}//computeAverageOfMidpointOfBarcodesWeightedByLength



bool compareForHistograms( const std::pair< double , std::pair<double,double> >& f , const std::pair< double , std::pair<double,double> >& s )
{
    return f.first < s.first;
}


void PersistenceBarcodes::putToAFileHistogramOfBarcodesLengths( char* filename , size_t howMany , bool shouldWeAlsoPutResponsibleBarcodes )
{
    std::vector<std::pair< double , std::pair<double,double> > > barsLenghts(this->barcodes.size());
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        barsLenghts[i] = std::make_pair(fabs(this->barcodes[i].second - this->barcodes[i].first) , std::make_pair( this->barcodes[i].first , this->barcodes[i].second ) );
    }
    std::sort( barsLenghts.begin() , barsLenghts.end() , compareForHistograms );
    std::reverse( barsLenghts.begin() , barsLenghts.end() );
    std::ofstream file;
    file.open(filename);
    if ( shouldWeAlsoPutResponsibleBarcodes )
    {
        for ( size_t i = 0 ; i != minn(barsLenghts.size(),howMany) ; ++i )
        {
            file << i << " " << barsLenghts[i].first << " " << barsLenghts[i].second.first << " " << barsLenghts[i].second.second << std::endl;
        }
    }
    else
    {
        for ( size_t i = 0 ; i != minn(barsLenghts.size(),howMany) ; ++i )
        {
            file << i << " " << barsLenghts[i].first << std::endl;
        }
    }
    file.close();
}//putToAFileHistogramOfBarcodesLengths


void PersistenceBarcodes::putToAFileHistogramOfBarcodesLengths( char* filename , size_t beginn , size_t endd , bool shouldWeAlsoPutResponsibleBarcodes )
{
    if ( beginn >= endd ){throw("Wrong parameters of putToAFileHistogramOfBarcodesLengths provedure. Begin points is greater that the end point. Program will now terminate");}
    std::vector<std::pair< double , std::pair<double,double> > > barsLenghts(this->barcodes.size());
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        barsLenghts[i] = std::make_pair(fabs(this->barcodes[i].second - this->barcodes[i].first) , std::make_pair( this->barcodes[i].first , this->barcodes[i].second ) );
    }
    std::sort( barsLenghts.begin() , barsLenghts.end() , compareForHistograms );
    std::reverse( barsLenghts.begin() , barsLenghts.end() );
    std::ofstream file;
    file.open(filename);
    if ( shouldWeAlsoPutResponsibleBarcodes )
    {
        for ( size_t i = minn(barsLenghts.size(),beginn) ; i != minn(barsLenghts.size(),endd) ; ++i )
        {
            file << i << " " << barsLenghts[i].first << " " << barsLenghts[i].second.first << " " << barsLenghts[i].second.second << std::endl;
        }
    }
    else
    {
        for ( size_t i = minn(barsLenghts.size(),beginn) ; i != minn(barsLenghts.size(),endd) ; ++i )
        {
            file << i << " " << barsLenghts[i].first << std::endl;
        }
    }
    file.close();
    /*
    std::vector<double> barsLenghts(this->barcodes.size());
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        barsLenghts[i] = fabs(this->barcodes[i].second - this->barcodes[i].first);
    }
    std::sort( barsLenghts.begin() , barsLenghts.end() );
    std::reverse( barsLenghts.begin() , barsLenghts.end() );
    std::ofstream file;
    file.open(filename);
    for ( size_t i = minn(barsLenghts.size(),beginn) ; i != minn(barsLenghts.size(),endd) ; ++i )
    {
        file << i << " " << barsLenghts[i] << std::endl;
    }
    file.close();
    */
}//putToAFileHistogramOfBarcodesLengths


void PersistenceBarcodes::removeShortBarcodes( double minimalDiameterOfBarcode )
{
    std::vector< std::pair<double,double> > cleanedBarcodes;
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        if ( fabs(this->barcodes[i].second - this->barcodes[i].first) > minimalDiameterOfBarcode )
        {
            cleanedBarcodes.push_back(this->barcodes[i]);
        }
    }
    this->barcodes.swap( cleanedBarcodes );
}


PersistenceBarcodes PersistenceBarcodes::restrictBarcodesToGivenInterval( std::pair<double,double> interval )
{
    PersistenceBarcodes result;
    result.dimensionOfBarcode = this->dimensionOfBarcode;
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        if ( this->barcodes[i].first >= interval.second )continue;
        if ( this->barcodes[i].second <= interval.first )continue;
        result.barcodes.push_back( std::make_pair( std::max( interval.first , this->barcodes[i].first ) , std::min( interval.second , this->barcodes[i].second ) ) );
    }
    return result;
}


PersistenceBarcodes::PersistenceBarcodes(const PersistenceBarcodes& orgyginal)
{
    this->dimensionOfBarcode = orgyginal.dimensionOfBarcode;
    this->barcodes.insert( this->barcodes.end() , orgyginal.barcodes.begin() , orgyginal.barcodes.end() );
}

PersistenceBarcodes PersistenceBarcodes::operator=( const PersistenceBarcodes& rhs )
{
    //std::cout << "Before : " << this->barcodes.size() << "\n";

    this->dimensionOfBarcode = rhs.dimensionOfBarcode;
    this->barcodes.clear();
    this->barcodes.insert( this->barcodes.begin() , rhs.barcodes.begin() , rhs.barcodes.end() );

    //std::cout << "after : " << this->barcodes.size() << "\n";
    //std::cin.ignore();

    return *this;
}


std::pair<double,double> PersistenceBarcodes::minMax()const
{
    double bmin = INT_MAX;
    double bmax = INT_MIN;
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        if ( this->barcodes[i].first < bmin )bmin = this->barcodes[i].first;
        if ( this->barcodes[i].second > bmax )bmax = this->barcodes[i].second;
    }
    return std::make_pair( bmin , bmax );
}//minMax

double PersistenceBarcodes::computeLandscapeIntegralFromBarcodes()
{
    double result = 0;
    for ( size_t i = 0 ; i != this->barcodes.size() ; ++i )
    {
        result += (this->barcodes[i].second-this->barcodes[i].first)*(this->barcodes[i].second-this->barcodes[i].first);
    }
    result *= 0.25;
    return result;
}





//TODO2 -- consider adding some instructions to remove anything that is not numeric from the input stream.
PersistenceBarcodes::PersistenceBarcodes(const char* filename)
{
    //cerr << "PersistenceBarcodes::PersistenceBarcodes(const char* filename) \n";
    this->dimensionOfBarcode = 0;
    std::ifstream read;
    read.open(filename);
    if ( !read.good() )
    {
        std::ostringstream errMessage;
	std::cerr <<"In constructor PersistenceBarcodes(const char* filename). Filename " << filename << " do not exist \n";
        errMessage <<"In constructor PersistenceBarcodes(const char* filename). Filename " << filename << " do not exist \n";
        std::string errMessageStr = errMessage.str();
        const char* err = errMessageStr.c_str();
        throw( err );
    }
    else
    {
        while ( read.good() )
        {
            double begin, end;

            //old version of the code to read persistence intervals. The problem here was that if the file was not ended with a new line, then the last barcode was not read
            //or (after some modifications) was read twice. The new code deals with this problem.
            //read >> begin;
            //read >> end;
            //if ( !read.good() )break;

            std::string line;
            std::getline(read, line);

            if ( line.size() )
            {
	        std::stringstream s;
                s << line;
                s >> begin;
                s >> end;
            }
            else
            {
                break;
            }





            if ( (!areThereInfiniteIntervals) && (end != infty) )
            {
                if ( end < begin )
                {
                    double z =end;
                    end = begin;
                    begin = z;
                }
                if ( begin != end )
                {
                    //TODO -- if you want to cut the data, comment the line in below.
                    this->barcodes.push_back( std::make_pair( begin,end ) );
                    //TODO - This is a correction that allows cutting of all the bars which born before whereToCut value.
                    /*
                    double whereToCut = 2;
                    if ( end > whereToCut )
                    {
                        if ( begin > whereToCut )
                        {
                            this->barcodes.push_back( std::make_pair( begin,end ) );
                        }
                        else
                        {
                            //in this case begin <= whereToCut and end > whereToCut
                            this->barcodes.push_back( std::make_pair( whereToCut,end ) );
                        }
                    }
                    */
                }
            }
            else
            {
                //we have here infinite interval.
                if ( !shallInfiniteBarcodesBeIgnored )
                {
                    this->barcodes.push_back( std::make_pair( begin,valueOfInfinity ) );
                }
            }
        }
        read.close();
    }
}

PersistenceBarcodes::PersistenceBarcodes(const char* filename , double bbegin , double step)
{
    extern double infty;
    this->dimensionOfBarcode = 0;
    std::ifstream read;
    read.open(filename);
    if ( !read.good() )
    {
        std::ostringstream errMessage;
        errMessage <<"In constructor PersistenceBarcodes(const char* filename). Filename " << filename << " do not exist \n";
        std::string errMessageStr = errMessage.str();
        const char* err = errMessageStr.c_str();
        throw( err );
    }
    while ( read.good() )
    {
        double begin, end;
        read >> begin;
        read >> end;

        if ( end != infty )
        {
            if ( end < begin )
            {
                double z =end;
                end = begin;
                begin = z;
            }
            if ( !read.good() )break;
            if ( begin != end )
            {
                this->barcodes.push_back( std::make_pair( bbegin+begin*step,bbegin+end*step ) );
            }
        }
         /*
        else
        {
            //we have here infinite interval:
            this->barcodes.push_back( std::make_pair( begin,INT_MAX ) );
        }*/
    }
    read.close();
}

PersistenceBarcodes::PersistenceBarcodes( std::vector< std::pair<double,double> > bars )
{
    extern double infty;
    this->dimensionOfBarcode = 0;
    unsigned sizeOfBarcode = 0;
    for ( size_t i = 0 ; i != bars.size() ; ++i )
    {
        if ( bars[i].second != infty )
        {
            ++sizeOfBarcode;
        }
        if ( bars[i].second < bars[i].first )
        {
            double sec = bars[i].second;
            bars[i].second = bars[i].first;
            bars[i].first = sec;
        }
    }
    std::vector< std::pair<double,double> > barcodes( sizeOfBarcode );
    unsigned nr = 0;
    for ( size_t i = 0 ; i != bars.size() ; ++i )
    {
        if ( bars[i].second != infty )
        {
            //this is a finite interval
            barcodes[nr] =  std::make_pair( bars[i].first , bars[i].second );
            ++nr;
        }
        //to keep it all compact for now I am removing infinite intervals from consideration.
        /*else
        {
            //this is infinite interval:
            barcodes[i] =  std::make_pair( bars[i].first , INT_MAX );
        }*/
    }
    //CHANGE
    //this->barcodes = barcodes;
    this->barcodes.swap( barcodes );
}


PersistenceBarcodes::PersistenceBarcodes(const char* filename , unsigned dimensionOfBarcode)
{
    *this = PersistenceBarcodes(filename);
    this->dimensionOfBarcode = dimensionOfBarcode;
}

PersistenceBarcodes::PersistenceBarcodes( std::vector< std::pair<double,double> > vect , unsigned dimensionOfBarcode)
{
    *this = PersistenceBarcodes(vect);
    this->dimensionOfBarcode = dimensionOfBarcode;
}


//this function ocmpute L^p bottleneck distance beteen diagrams.
bool computeBottleneckDistanceDBG = false;
std::pair< double , std::vector< std::pair< std::pair<double,double> , std::pair<double,double> > > > computeBottleneckDistance( const PersistenceBarcodes& first, const PersistenceBarcodes& second , unsigned p  )
{
   //If first and second have different sizes, then I want to rename them in the way that first is the larger one:
   std::vector< std::pair<double,double> > firstBar;
   std::vector< std::pair<double,double> > secondBar;

   firstBar.insert( firstBar.end() , first.barcodes.begin() , first.barcodes.end() );
   secondBar.insert( secondBar.end() , second.barcodes.begin() , second.barcodes.end() );

   if ( computeBottleneckDistanceDBG )
   {
       std::cerr << "firstBar.size()  : " << firstBar.size() << std::endl;
       std::cerr << "secondBar.size()  : " << secondBar.size() << std::endl;
       std::cin.ignore();
   }

   int ** Array = new int*[(firstBar.size()+secondBar.size())];
   char** Result = new char*[(firstBar.size()+secondBar.size())];
   for ( size_t i = 0 ; i != (firstBar.size()+secondBar.size()) ; ++i )
   {
       Result[i] = new char[(firstBar.size()+secondBar.size())];
       Array[i] = new int[(firstBar.size()+secondBar.size())];
   }
   //to illustrate how the matrix is create let us look at the following example. Suppose one set of bars consist of two points A, B, and another consist of a single point C.
   //The matrix should look like this in that case:
   //       |      A       |      B      |  diag( C )  |
   //  C    |    d(A,C)    |   d(A,B)    | d(C,diag(C))|
   //diag(A)| d(A,diag(A)) |    0        |  0          |
   //diag(B)|     0        |d(B,diag(B)) |  0          |
   //
   //Therefore as one can clearly see, the matrix can be parition in to 4 essential parts:
   //    P1 | P2
   //    P3 | P4
   //Where:
   //P1 -- submatrix of distances between points
   //P2 -- Distances from 'barcodes C' to diagonal
   //P3 -- distances from 'barcodes a&B' to diagonal
   //P4 -- matrix of zeros.

   //this implementation of Hungarian algorithm accepts only int's. That is why I converge all the double numbers here to ints by multipling by this big number:
   int bigNumber = 10000;

   if (computeBottleneckDistanceDBG)std::cerr << "Starting creation of cost matrix \n";

   for ( size_t coll = 0 ; coll != (firstBar.size()+secondBar.size()) ; ++coll )
   {
       for ( size_t row = 0 ; row != (firstBar.size()+secondBar.size()) ; ++row )
       {
           if (computeBottleneckDistanceDBG)std::cerr << "row = " << row << "\n" << "coll : " << coll << "\n";
           if ( ( coll < firstBar.size() ) && ( row < secondBar.size() ) )
           {
               //P1
               Array[coll][row] = (int)bigNumber*pow((double)computeDistanceOfPointsInPlane( firstBar[coll] , secondBar[row] ),(double)p);
               if (computeBottleneckDistanceDBG)
               {
                    std::cerr << "Region P1, computing distance between : " << firstBar[coll] << " and " << secondBar[row] << "\n";
                    std::cerr << "The distance is : " << Array[coll][row] << std::endl;
                    std::cerr << "The distance is : " << computeDistanceOfPointsInPlane( firstBar[coll] , secondBar[row] ) << std::endl;
               }
           }
           if ( (coll >= firstBar.size()) && (row < secondBar.size()) )
           {
               //P2
               //distance between point from secondBar and its projection to diagonal
                Array[coll][row] = (int)bigNumber*pow(computeDistanceOfPointsInPlane( secondBar[row] , projectionToDiagonal(secondBar[coll - firstBar.size()]) ),(double)p);
                if (computeBottleneckDistanceDBG)
                {
                    std::cerr << "Region P2, computing distance between : " << secondBar[row] << " and projection(" <<secondBar[coll - firstBar.size()] << ") which is : "  << projectionToDiagonal(secondBar[coll - firstBar.size()]) << "\n";
                    std::cerr << "The distance is : " << Array[coll][row] << std::endl;
                }
           }
           if ( (coll < firstBar.size()) && (row >= secondBar.size()) )
           {
              //distance between point from firstBar and its projection to diagonal
              Array[coll][row] = (int)bigNumber*pow(computeDistanceOfPointsInPlane( firstBar[coll] , projectionToDiagonal(firstBar[row-secondBar.size()]) ),(double)p);
              if (computeBottleneckDistanceDBG)
              {
                  std::cerr << "Region P3, computing distance between : " << firstBar[coll] << " and projection(" << firstBar[row-secondBar.size()] << ") which is :  " << projectionToDiagonal(firstBar[row-secondBar.size()]) << "\n";
                  std::cerr << "The distance is : " << Array[coll][row] << std::endl;
              }
           }
           if ( (coll >= firstBar.size()) && (row >= secondBar.size()) )
           {
               //P4
               if (computeBottleneckDistanceDBG)
                        std::cout << "Region P4, set to infinitey \n";
               Array[coll][row] = 0;
           }
           if (computeBottleneckDistanceDBG)std::cin.ignore();
       }
   }

   if (computeBottleneckDistanceDBG)
   {
       for ( size_t i = 0 ; i != (firstBar.size()+secondBar.size()) ; ++i )
       {
           for ( size_t j = 0 ; j != (firstBar.size()+secondBar.size()) ; ++j )
           {
               std::cout << Array[i][j] << "  ";
           }
           std::cout << "\n";
       }
       std::cout << "Matrix has been created\n"; std::cin.ignore();
   }



    int cost = hungarian(Array,Result,(firstBar.size()+secondBar.size()),(firstBar.size()+secondBar.size()));
    if (computeBottleneckDistanceDBG)
    {
        for (int y=0;y<(firstBar.size()+secondBar.size());++y)
        {
          for (int x=0;x<(firstBar.size()+secondBar.size());++x)
          {
            std::cout << (int)Result[y][x] << " ";
          }
          std::cout << "\n";
        }
    }

    std::vector< std::pair< std::pair<double,double> , std::pair<double,double> > > matching;

    for (int y=0;y<(firstBar.size()+secondBar.size());++y)
    {
      for (int x=0;x<(firstBar.size()+secondBar.size());++x)
      {
           if ( Result[x][y] )
           {
               bool store = false;
               if ( x < firstBar.size() )
               {
                    if (computeBottleneckDistanceDBG){std::cout << firstBar[x] << "  ";}
                    store = true;
               }
               else
               {
                    if (computeBottleneckDistanceDBG){std::cout << "projection(" << secondBar[x - firstBar.size()] << ")  ";}
               }
               if (computeBottleneckDistanceDBG){std::cout << " is paired with ";}
               if ( y < secondBar.size() )
               {
                    if (computeBottleneckDistanceDBG){std::cout << secondBar[y];}
                    store = true;
               }
               else
               {
                    if (computeBottleneckDistanceDBG){std::cout << "projection(" << firstBar[y - secondBar.size()] << ")  ";}
               }
               if (computeBottleneckDistanceDBG){std::cout << "\n\n";}

               if ( store )
               {
                   //at least one element in not from diagonal:
                   matching.push_back( std::make_pair(firstBar[x] , secondBar[y]) );
               }
           }
      }
    }

    for ( size_t i = 0 ; i != (firstBar.size()+secondBar.size()) ; ++i )
    {
        delete Array[i];
        delete Result[i];
    }
    delete [] Array;
    delete [] Result;
    std::pair< double , std::vector< std::pair< std::pair<double,double>,std::pair<double,double> > > > result = std::make_pair( pow(cost/(double)bigNumber,1/(double)p) , matching );
    return result;
}


#endif
