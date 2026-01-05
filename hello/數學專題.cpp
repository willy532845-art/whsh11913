#include <bits/stdc++.h>
using namespace std;

long long r;
set<long long> vis;

long long f(long long x) {
     return 3 * x + 1;
     }
long long g(long long x) {
     return 5 * x;
     }

vector<function<long long(long long)>> funcs = {f, g};

void dfs(long long x) {
    if (x >= r) return;
    if (vis.count(x)) return;

    vis.insert(x);

    for (auto func : funcs) {
        dfs(func(x));
    }
}

int main() {
    long long n;
    cin >> n >> r;

    dfs(n);

    for (long long x : vis)
        cout << x << '\n';

    return 0;
}
