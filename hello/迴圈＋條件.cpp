#include<bits/stdc++.h>
using namespace std;

int main(){
    int N;
    int a=0;
    cin>>N;
    for(int i=1;i<=N;i++){
        if(i%3==0&&i%5!=0){
            a++;
        }
    }
    cout<<a;
    return 0;
}
