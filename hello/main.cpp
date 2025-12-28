#include <iostream>
using namespace std;

int main() {
    int day;
    cout << "Enter day (1-7): ";
    cin >> day;

    switch (day) {
        case 1: cout << "Mon\n"; break;
        case 2: cout << "Tue\n"; break;
        case 3: cout << "Wed\n"; break;
        case 4: cout << "Thu\n"; break;
        case 5: cout << "Fri\n"; break;
        case 6: cout << "Sat\n"; break;
        case 7: cout << "Sun\n"; break;
        default: cout << "Invalid (1-7)\n";
    }

    cin.ignore();
    cin.get();
    return 0;
}
