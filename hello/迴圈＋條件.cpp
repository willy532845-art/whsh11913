#include <bits/stdc++.h>
using namespace std;

int main() {
    int N, M;
    cin >> N >> M;

    int a[N + 1] = {0};

    for (int j = 0; j < M; j++) {
        int K;
        cin >> K;
        for (int i = K; i <= N; i += K) {
            a[i] = 1 - a[i];
        }
    }

    int cou = 0;
    for (int i = 1; i <= N; i++) {
        if (a[i] == 1) cou++;
    }

    cout << cou;
    return 0;
}
