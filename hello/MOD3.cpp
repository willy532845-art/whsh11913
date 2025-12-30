#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;

    int j = 0, k = 0, l = 0;

    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        int mod = x % 3;

        switch (mod) {
            case 0: j++; break;
            case 1: k++; break;
            case 2: l++; break;
        }
    }

    cout << j << " " << k << " " << l << "\n";
    return 0;
}
