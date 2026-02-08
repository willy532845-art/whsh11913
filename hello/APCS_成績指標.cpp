#include<bits/stdc++.h>
using namespace std;

int main(){
    int n,x,pt=0,ft=0,maf=0,mnp=100;
    vector<int> p;
    vector<int> f;
    vector<int> all;
    cin>>n;
    for(int i=1;i<=n;i++){
        cin>>x;
        all.push_back(x);

        if(x>=60){
            p.push_back(x);
            pt++;
        }else{
            f.push_back(x);
            ft++;
        }
    }
    for (int i = 0; i < (int)f.size(); i++) {
            maf = max(maf, f[i]);
    }
    for (int i = 0; i < (int)p.size(); i++) {
        mnp = min(mnp, p[i]);
    }
    sort(all.begin(), all.end());
    for (int i = 0; i < (int)all.size(); i++) {
        if (i) cout << " ";
        cout << all[i];
    }
    cout << "\n";
if (ft == 0) cout << "best case\n";
else cout << maf << "\n";
if (pt == 0) cout << "worst case\n";
else cout << mnp << "\n";
}
