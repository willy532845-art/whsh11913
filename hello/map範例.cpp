#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<int> a(n);
    for (int i = 0; i < n; i++) cin >> a[i];

    if (n < 3) {
        cout << "NO\n";
        return 0;
    }

    // rightMax[i] = i 娩( i+1..n-1 )程
    vector<int> rightMax(n, INT_MIN);
    int mx = a[n - 1];
    for (int i = n - 2; i >= 0; i--) {
        rightMax[i] = mx;        // i 娩程
        mx = max(mx, a[i]);      // 穝ヘ玡筁程
    }

    int minLeft = a[0];          // j オ娩(0..j-1)程
    for (int j = 1; j <= n - 2; j++) {
        if (minLeft < a[j] && a[j] < rightMax[j]) {
            cout << "YES\n";
            return 0;
        }
        minLeft = min(minLeft, a[j]);  // 穝オ娩程
    }

    cout << "NO\n";
    return 0;
}
