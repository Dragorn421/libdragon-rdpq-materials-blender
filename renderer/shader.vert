uniform mat4 matMVP;
uniform mat4 matMV;

in vec3 inPos;
in vec3 inNormal;
in vec4 inColor;

out vec4 shadeColor;

void main()
{
    gl_Position = matMVP * vec4(inPos, 1.0);
    float i = max(0, dot(mat3(matMV) * inNormal, vec3(0, 0, 1)));
    shadeColor = inColor * vec4(i, i, i, 1.0);
}
