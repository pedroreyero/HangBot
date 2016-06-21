x_top = linspace(-a/2, a/2, 10);
y_top = ones(1,10) * b/2;

x_bottom = linspace(-a/2, a/2, 10);
y_bottom = ones(1,10) * -b/2;

y_left = linspace(-b/2, b/2, 10);
x_left = ones(1,10) * -a/2;

y_right = linspace(-b/2, b/2, 10);
x_right = ones(1,10) * a/2;


plot(x_top, y_top, 'c');
hold on
axis equal
plot(x_bottom, y_bottom, 'c');
plot(x_left, y_left, 'c');
plot(x_right, y_right, 'c');