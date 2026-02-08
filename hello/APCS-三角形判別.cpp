#include<bits/stdc++.h>
using namespace std;

int main(){
    int a,b,c,big,no,small;
    int big2,no2,small2;
    cin>>a>>b>>c;
    if(a>b&&a>c){
        big=a;
        if(b>c){
            no=b;
            small=c;
        }else{
            small=b;
            no=c;
        }
    }else if(b>a&&b>c){
        big=b;
        if(a>c){
            no=a;
            small=c;
        }else{
            small=a;
            no=c;
        }
    }else if(c>b&&c>a){
        big=c;
        if(a>b){
            no=a;
            small=b;
        }else{
            small=a;
            no=b;
        }
    }
    big2=big^2;
    no2=no^2;
    small2=small^2;
    cout<<small<<" "<<no<<" "<<big<<endl;
    if(small+no<=big){
        cout<<"No";
    }else if(small2+no2<big2){
        cout<<"Obtuse";
    }else if(small2+no2==big2){
        cout<<"Right";
    }else if(small2+no2>big2){
        cout<<"Acute";
    }
    return 0;
    }
