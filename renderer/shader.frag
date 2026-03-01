uniform vec4 color;

in vec4 shadeColor;

out vec4 FragColor;

void main() 
{
    FragColor = color * shadeColor;
}
