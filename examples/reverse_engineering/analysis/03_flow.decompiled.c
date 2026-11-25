/*
 * 03_flow — Ghidra 12.2가 생성한 C 의사 코드와 분석 주석
 *
 * 대상 ELF  SHA-256  642ca95a3d26eeb7ad616600a7f45c2bb0c1c48f77f8639f68c1c75912cb8fe6
 * 빌드      examples/reverse_engineering/Makefile, GCC 13.3.0, -O0 -g, x86-64 PIE
 * 분석      Ghidra 기본 자동 분석으로 C 예제 함수 6개를 디컴파일했다.
 * 검증      objdump -d -M intel, 동일 ELF 직접 실행, 원본 03_flow.c 대조
 * 주소      Ghidra 이미지 베이스는 0x00100000이다.
 *           아래 주석의 objdump 주소에 이미지 베이스를 더하면 Ghidra 주소가 된다.
 *
 * 재현
 *   make -C examples/reverse_engineering build/03_flow
 *   objdump -d -M intel examples/reverse_engineering/build/03_flow
 *   ./examples/reverse_engineering/build/03_flow
 *
 * 관찰한 표준 출력과 종료 상태
 *   add_bias(4,5)=12
 *   signed(-1)=1 unsigned(UINT_MAX)=0
 *   sum_to(0)=0 sum_to(1)=0 sum_to(4)=6
 *   mix_bits(0x23)=242
 *   종료 코드 0
 *
 * Ghidra에서 보려면 같은 디렉터리의 03_flow.gzf를 프로젝트에 가져온 뒤
 * Symbol Tree의 Functions에서 각 함수를 연다.
 */

/* Ghidra 0x001011f7 */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* 가설 — 고정 인자로 다섯 보조 함수를 호출해 결과를 보여주는 실습
   진입점이다.
   검증 — Listing에서 직접 call 대상과 네 번의 printf 호출을 확인했다.
   실제 실행에서 출력 네 줄과 종료 코드 0을 확인했다.
   이 빌드에서는 sum_to를 4, 1, 0 순서로 호출하고 0, 1, 4 순서로 출력한다. */

int main(void)

{
  int iVar1;
  int param1;
  uint param3;
  uint param2;
  uint param1_00;
  uint32_t param1_01;

  iVar1 = add_bias(4,5);
  printf("add_bias(4,5)=%d\n",iVar1);
  iVar1 = choose_unsigned(0xffffffff);
  param1 = choose_signed(-1);
  printf("signed(-1)=%d unsigned(UINT_MAX)=%d\n",param1,iVar1);
  param3 = sum_to(4);
  param2 = sum_to(1);
  param1_00 = sum_to(0);
  printf("sum_to(0)=%u sum_to(1)=%u sum_to(4)=%u\n",param1_00,param2,param3);
  param1_01 = mix_bits(0x23);
  printf("mix_bits(0x23)=%u\n",param1_01);
  return 0;
}

/* Ghidra 0x00101149 */
/* 가설 — 정수 두 개의 합에 상수 3을 더한다.
   검증 — objdump 0x115d의 add eax,edx와 0x115f의 add eax,0x3을 확인했다.
   실행 결과는 add_bias(4,5)=12였다. 원본 03_flow.c 4~6행과 일치한다. */

int add_bias(int left,int right)

{
  int right_local;
  int left_local;

  return right + left + 3;
}

/* Ghidra 0x00101164 */
/* 가설 — 입력을 부호 있는 값으로 비교해 10 미만이면 1을 돌려준다.
   검증 — objdump 0x116f에서 9와 비교하고 0x1173의 jg로 0 반환 경로에 간다.
   부호 있는 비교에서 9 이하는 10 미만과 같다. 실행에서 signed(-1)=1이었다.
   원본 03_flow.c 8~13행은 if문이고, Ghidra는 비교식의 값을 바로 반환한다. */

int choose_signed(int value)

{
  int value_local;

  return (int)(value < 10);
}

/* Ghidra 0x00101183 */
/* 가설 — 같은 비트 패턴을 부호 없는 값으로 해석하면 비교 결과가
   달라진다.
   검증 — objdump 0x118e에서 9와 비교하고 0x1192의 ja로 0 반환 경로에 간다.
   main은 두 비교 함수에 모두 0xffffffff를 넘긴다. 여기서는 4294967295로
   해석되어
   실행에서 unsigned(UINT_MAX)=0이었다. 원본 03_flow.c 15~20행과 일치한다. */

int choose_unsigned(uint value)

{
  uint value_local;

  return (int)(value < 10);
}

/* Ghidra 0x001011a2 */
/* 가설 — 0부터 limit 직전까지 더하고, limit이 0이면 반복문에 들어가지
   않는다.
   검증 — objdump 0x11bb에서 조건 검사로 먼저 이동한다. 0x11cd의 jb가
   index < limit일 때 합산 위치 0x11bd로 돌아간다. 실행에서 0, 1, 4를 넘긴
   결과는 각각 0, 0, 6이었다. 원본 03_flow.c 22~28행과 일치한다. */

uint sum_to(uint limit)

{
  uint limit_local;
  uint total;
  uint index;

  total = 0;
  for (index = 0; index < limit; index = index + 1) {
    total = total + index;
  }
  return total;
}

/* Ghidra 0x001011d4 */
/* 가설 — 입력의 하위 바이트를 섞은 값과 입력을 4비트 우측 이동한 값을
   OR한다.
   검증 — objdump 0x11e2~0x11e9에서 두 배, 0x1fe 마스크, 0xb4 XOR를 확인했다.
   0x11f0의 shr와 0x11f3의 or를 확인했다. 원본 03_flow.c 30~32행의
   0xff 마스크와 0x5a XOR 뒤에 붙은 좌측 이동을 먼저 적용하면 같은 식이다.
   0x23에서 0xf2 | 0x02 = 0xf2를 계산했고, 실행 출력은 242였다. */

uint32_t mix_bits(uint32_t value)

{
  uint32_t value_local;

  return value >> 4 | value * 2 & 0x1fe ^ 0xb4;
}
