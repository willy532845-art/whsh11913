#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    set<int> seen;

    for (int i = 0; i < n; i++) {
        int x; cin >> x;
        if (seen.count(x)) {
            cout << "有重複\n";
            return 0;
        }
        seen.insert(x);
    }
    cout << "沒有重複\n";
    return 0;
}
